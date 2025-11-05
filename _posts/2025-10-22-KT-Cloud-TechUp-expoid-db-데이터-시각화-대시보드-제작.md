---
layout: post
title: "[KT Cloud TechUp] expoid_db 데이터 시각화 대시보드 제작"
date: 2025-10-22 01:28:15 +0900
categories: velog
series: "kt cloud techup"
thumbnail: "/assets/images/hosooinmymind/images/hosooinmymind/post/143f08aa-731a-4411-95c9-03e1cd15147b/image.png"
---

<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/143f08aa-731a-4411-95c9-03e1cd15147b/image.png"/>우선은 phpmyadmin에서 테이블을 제작하고 간단한 테스트 데이터들을 넣어두었다.</p>
<p>[php란?]</p>
<ul>
<li>오픈소스 언어로 데이터베이스와 연동이 간편한 언어이다.<pre><code>&lt;?php
echo "Hello, World!";
$name = "홍길동";
echo "안녕하세요," . $name . "님!";
</code></pre></li>
</ul>
<p>//html과 결합
?&gt;</p>
<h1>의 페이지</h1>
```
- 주요 용도: 웹 개발 (동적 웹페이지 생성), CMS (WordPress, Drupal 등), 웹 애플리케이션 (쇼핑몰, 게시판 등), API 개발 (RESTful API 구축)



<pre><code>&lt;?php
// visualize_exploits.php
// Usage: configure MySQL credentials below and place this file on a PHP-enabled webserver.
// Expected MySQL table structure (example):
// CREATE TABLE exploits (
//   id INT AUTO_INCREMENT PRIMARY KEY,
//   date VARCHAR(50),
//   url TEXT,
//   title TEXT,
//   access_type VARCHAR(100),
//   platform VARCHAR(100),
//   author VARCHAR(100),
//   cve VARCHAR(100)
// );

// ---------- Configuration: edit these ----------
$dbHost = '127.0.0.1';
$dbName = 'mysql_251021';
$dbUser = 'root';
$dbPass = '';
$dbTable = 'exploitdb'; // table name
$perPage = 100; // rows per page for pagination
// -----------------------------------------------

// PDO connection
$dsn = "mysql:host={$dbHost};dbname={$dbName};charset=utf8mb4";
try {
    $pdo = new PDO($dsn, $dbUser, $dbPass, [
        PDO::ATTR_ERRMODE =&gt; PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE =&gt; PDO::FETCH_ASSOC,
    ]);
} catch (Exception $e) {
    echo "&lt;h2&gt;DB 연결 실패:&lt;/h2&gt;" . htmlspecialchars($e-&gt;getMessage());
    exit;
}

// paging
$page = isset($_GET['page']) ? max(1, (int)$_GET['page']) : 1;
$offset = ($page - 1) * $perPage;

// basic search filter
$q = isset($_GET['q']) ? trim($_GET['q']) : '';
$params = [];
$where = '';
if ($q !== '') {
    // search in title, author, cve, platform
    $where = "WHERE title LIKE :q OR author LIKE :q OR cve LIKE :q OR platform LIKE :q";
    $params[':q'] = "%{$q}%";
}

// count total
$countSql = "SELECT COUNT(*) AS cnt FROM `{$dbTable}` {$where}";
$stmt = $pdo-&gt;prepare($countSql);
$stmt-&gt;execute($params);
$total = (int)$stmt-&gt;fetchColumn();
$totalPages = max(1, (int)ceil($total / $perPage));

// fetch rows
$sql = "SELECT date, url, title, access_type, platform, author, cve
        FROM `{$dbTable}` {$where}
        ORDER BY date DESC
        LIMIT :limit OFFSET :offset";
$stmt = $pdo-&gt;prepare($sql);
foreach ($params as $k =&gt; $v) $stmt-&gt;bindValue($k, $v, PDO::PARAM_STR);
$stmt-&gt;bindValue(':limit', (int)$perPage, PDO::PARAM_INT);
$stmt-&gt;bindValue(':offset', (int)$offset, PDO::PARAM_INT);
$stmt-&gt;execute();
$rows = $stmt-&gt;fetchAll();

// aggregates for charts
$byPlatform = [];
$byAuthor = [];
$byYear = [];
foreach ($rows as $r) {
    $p = $r['platform'] ?: 'Unknown';
    $byPlatform[$p] = ($byPlatform[$p] ?? 0) + 1;

    $a = $r['author'] ?: 'Unknown';
    $byAuthor[$a] = ($byAuthor[$a] ?? 0) + 1;

    $year = 'Unknown';
    if (preg_match('/(\d{4})/', $r['date'], $m)) {
        $year = $m[1];
    } else {
        $ts = strtotime($r['date']);
        if ($ts) $year = date('Y', $ts);
    }
    $byYear[$year] = ($byYear[$year] ?? 0) + 1;
}

arsort($byPlatform);
arsort($byAuthor);
ksort($byYear);

function h($s) { return htmlspecialchars($s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
?&gt;
&lt;!doctype html&gt;
&lt;html lang="ko"&gt;
&lt;head&gt;
    &lt;meta charset="utf-8"&gt;
    &lt;meta name="viewport" content="width=device-width,initial-scale=1"&gt;
    &lt;title&gt;Exploit DB 시각화 (MySQL)&lt;/title&gt;
    &lt;style&gt;
        body{font-family:Inter,system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; padding:20px;}
        table{border-collapse:collapse;width:100%;}
        th,td{border:1px solid #ddd;padding:8px;text-align:left;font-size:13px}
        th{background:#f3f4f6}
        .grid{display:grid;grid-template-columns:1fr 420px;gap:20px}
        .card{background:#fff;border:1px solid #e5e7eb;padding:12px;border-radius:8px}
        .controls{margin-bottom:12px}
        input[type=search]{padding:8px;width:100%;box-sizing:border-box}
        .small{font-size:12px;color:#6b7280}
        .pager{margin-top:8px}
        .pager a{margin-right:6px;text-decoration:none}
        @media(max-width:900px){.grid{grid-template-columns:1fr}}
    &lt;/style&gt;
    &lt;script src="https://cdn.jsdelivr.net/npm/chart.js"&gt;&lt;/script&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;h1&gt;Exploit 데이터 (MySQL) 시각화&lt;/h1&gt;
    &lt;p class="small"&gt;전체 레코드: &lt;strong&gt;&lt;?php echo $total; ?&gt;&lt;/strong&gt;&lt;/p&gt;

    &lt;form method="get" class="controls" style="max-width:600px"&gt;
        &lt;input type="search" name="q" placeholder="검색 (제목/저자/CVE/플랫폼)" value="&lt;?php echo h($q); ?&gt;"&gt;
        &lt;button type="submit"&gt;검색&lt;/button&gt;
    &lt;/form&gt;

    &lt;div class="grid"&gt;
        &lt;div&gt;
            &lt;div class="card" id="tableCard"&gt;
                &lt;table id="dataTable"&gt;
                    &lt;thead&gt;
                        &lt;tr&gt;
                            &lt;th&gt;날짜&lt;/th&gt;
                            &lt;th&gt;제목&lt;/th&gt;
                            &lt;th&gt;접근&lt;/th&gt;
                            &lt;th&gt;플랫폼&lt;/th&gt;
                            &lt;th&gt;저자&lt;/th&gt;
                            &lt;th&gt;CVE&lt;/th&gt;
                        &lt;/tr&gt;
                    &lt;/thead&gt;
                    &lt;tbody&gt;
                        &lt;?php foreach ($rows as $r): ?&gt;
                        &lt;tr data-url="&lt;?php echo h($r['url']); ?&gt;"&gt;
                            &lt;td&gt;&lt;?php echo h($r['date']); ?&gt;&lt;/td&gt;
                            &lt;td&gt;&lt;?php echo h($r['title']); ?&gt;&lt;/td&gt;
                            &lt;td&gt;&lt;?php echo h($r['access_type']); ?&gt;&lt;/td&gt;
                            &lt;td&gt;&lt;?php echo h($r['platform']); ?&gt;&lt;/td&gt;
                            &lt;td&gt;&lt;?php echo h($r['author']); ?&gt;&lt;/td&gt;
                            &lt;td&gt;&lt;?php echo h($r['cve']); ?&gt;&lt;/td&gt;
                        &lt;/tr&gt;
                        &lt;?php endforeach; ?&gt;
                    &lt;/tbody&gt;
                &lt;/table&gt;

                &lt;div class="pager"&gt;
                    &lt;?php if ($page &gt; 1): ?&gt;
                        &lt;a href="?&lt;?php echo http_build_query(array_merge($_GET, ['page' =&gt; $page - 1])); ?&gt;"&gt;&amp;laquo; 이전&lt;/a&gt;
                    &lt;?php endif; ?&gt;
                    &lt;span&gt;페이지 &lt;?php echo $page; ?&gt; / &lt;?php echo $totalPages; ?&gt;&lt;/span&gt;
                    &lt;?php if ($page &lt; $totalPages): ?&gt;
                        &lt;a href="?&lt;?php echo http_build_query(array_merge($_GET, ['page' =&gt; $page + 1])); ?&gt;"&gt;다음 &amp;raquo;&lt;/a&gt;
                    &lt;?php endif; ?&gt;
                &lt;/div&gt;
            &lt;/div&gt;
        &lt;/div&gt;

        &lt;div&gt;
            &lt;div class="card"&gt;
                &lt;h3&gt;플랫폼 분포&lt;/h3&gt;
                &lt;canvas id="platformChart" width="400" height="300"&gt;&lt;/canvas&gt;
            &lt;/div&gt;

            &lt;div class="card" style="margin-top:12px"&gt;
                &lt;h3&gt;저자 상위&lt;/h3&gt;
                &lt;canvas id="authorChart" width="400" height="300"&gt;&lt;/canvas&gt;
            &lt;/div&gt;

            &lt;div class="card" style="margin-top:12px"&gt;
                &lt;h3&gt;연도별 발생 수&lt;/h3&gt;
                &lt;canvas id="yearChart" width="400" height="200"&gt;&lt;/canvas&gt;
            &lt;/div&gt;
        &lt;/div&gt;
    &lt;/div&gt;

    &lt;script&gt;
        const byPlatform = &lt;?php echo json_encode(array_values($byPlatform)); ?&gt;;
        const byPlatformLabels = &lt;?php echo json_encode(array_keys($byPlatform)); ?&gt;;

        const byAuthor = &lt;?php echo json_encode(array_values(array_slice($byAuthor,0,10))); ?&gt;;
        const byAuthorLabels = &lt;?php echo json_encode(array_keys(array_slice($byAuthor,0,10))); ?&gt;;

        const byYearLabels = &lt;?php echo json_encode(array_keys($byYear)); ?&gt;;
        const byYear = &lt;?php echo json_encode(array_values($byYear)); ?&gt;;

        new Chart(document.getElementById('platformChart'), {
            type: 'pie',
            data: { labels: byPlatformLabels, datasets: [{ data: byPlatform }] },
            options: {responsive:true}
        });

        new Chart(document.getElementById('authorChart'), {
            type: 'bar',
            data: { labels: byAuthorLabels, datasets: [{label:'발생 수', data: byAuthor}] },
            options: {responsive:true, scales:{y:{beginAtZero:true}}}
        });

        new Chart(document.getElementById('yearChart'), {
            type: 'line',
            data: { labels: byYearLabels, datasets: [{label:'건수', data: byYear, fill:false, tension:0.2}] },
            options: {responsive:true, scales:{y:{beginAtZero:true}}}
        });

        document.querySelectorAll('#dataTable tbody tr').forEach(tr =&gt; {
            tr.addEventListener('click', () =&gt; {
                const url = tr.dataset.url;
                if (url) window.open(url, '_blank');
            });
        });
    &lt;/script&gt;

    &lt;footer style="margin-top:18px;font-size:12px;color:#6b7280"&gt;
        MySQL에서 직접 데이터를 읽어 표와 차트를 생성합니다. DB 칼럼이나 테이블 이름이 다르면 상단 설정을 수정해주세요.
    &lt;/footer&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre><p>뼈대 코드는 위와 같다.</p>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/ddcfca1e-3b77-4b58-8ef5-e7683bf86bb1/image.png"/>
접속까지 완료했다.</p>
<p>db 연결을 해주자
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/2e8d150b-af54-46a0-87ef-41a58843690d/image.png"/></p>
<p>짠~</p>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/1bb012d5-85e2-4eff-88d1-0982a7aaadc6/image.png"/>
어제 만든 크롤링 코드와 연동까지 완료했다.
exploid-db 사이트에 있는 취약점을 긁어와서 시각화까지 해주는 대시보드 제작 완료.</p>
<p><a href="https://github.com/aneomagig/exploitdb_crawler_visualizer">https://github.com/aneomagig/exploitdb_crawler_visualizer</a></p>