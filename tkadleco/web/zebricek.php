<?php
// zebricek.php — Žebříček hry City Rescue Simulator
// Nahrajte do stejné složky jako index.html na váš školní server

$host = "dbs.spskladno.cz";
$db   = "vyuka14";
$user = "student14";
$pass = "spsnet";

$chyba = null;
$radky = [];

try {
    $pdo = new PDO("mysql:host=$host;dbname=$db;charset=utf8", $user, $pass);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Přijímání nového skóre z Python hry (POST request)
    if ($_SERVER['REQUEST_METHOD'] === 'POST'
        && isset($_POST['hrac'], $_POST['body'])
        && is_numeric($_POST['body']))
    {
        $stmt = $pdo->prepare(
            "INSERT INTO score_tabulka (hrac, body) VALUES (?, ?)"
        );
        $stmt->execute([
            htmlspecialchars(trim($_POST['hrac'])),
            (int)$_POST['body']
        ]);
        echo "ULOZENO";
        exit;
    }

    // Načtení top 20 výsledků pro zobrazení
    $stmt = $pdo->query(
        "SELECT hrac, body, datum
         FROM score_tabulka
         ORDER BY body DESC
         LIMIT 20"
    );
    $radky = $stmt->fetchAll(PDO::FETCH_ASSOC);

} catch (PDOException $e) {
    $chyba = "Nelze načíst žebříček: " . $e->getMessage();
}
?>
<!DOCTYPE html>
<html lang="cs">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Žebříček — City Rescue Simulator</title>
  <link rel="stylesheet" href="style.css">
  <style>
    .zebricek-hero {
      background: linear-gradient(135deg, #0a0a18, #0e1830);
      padding: 60px 40px 40px;
      text-align: center;
    }
    .zebricek-hero h1 { font-size: 2.8rem; margin-bottom: 10px; }
    .zebricek-hero p  { color: #7878a0; }

    .zebricek-wrap {
      max-width: 800px; margin: 0 auto; padding: 50px 24px;
    }

    .chyba-box {
      background: rgba(220,48,48,0.15);
      border: 1px solid rgba(220,48,48,0.4);
      border-radius: 10px; padding: 20px 24px;
      color: #ff8080; margin-bottom: 30px;
    }

    .prazdny {
      text-align: center; padding: 60px;
      color: #7878a0; font-size: 1.1rem;
    }

    .score-table {
      width: 100%; border-collapse: collapse;
      background: #1a1a2e;
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 14px; overflow: hidden;
    }
    .score-table th {
      background: #12121e;
      padding: 14px 20px;
      text-align: left;
      font-size: 0.85rem;
      color: #7878a0;
      text-transform: uppercase;
      letter-spacing: .06em;
    }
    .score-table td {
      padding: 14px 20px;
      border-top: 1px solid rgba(255,255,255,0.06);
      font-size: 0.95rem;
    }
    .score-table tr:hover td { background: rgba(255,255,255,0.03); }

    /* Pořadí */
    .rank { font-weight: 700; width: 52px; }
    .rank-1 { color: #ffd700; font-size: 1.1rem; }
    .rank-2 { color: #c0c0c0; font-size: 1.05rem; }
    .rank-3 { color: #cd7f32; }

    /* Skóre */
    .score-val { font-weight: 700; color: #e8a020; }

    /* Datum */
    .datum-val { color: #7878a0; font-size: 0.85rem; }

    .zpet-btn {
      display: inline-block; margin-bottom: 30px;
      padding: 10px 24px; border-radius: 8px;
      background: #1a1a2e; border: 1px solid rgba(255,255,255,0.1);
      color: #e8e8f0; text-decoration: none; font-size: 0.9rem;
      transition: background .2s;
    }
    .zpet-btn:hover { background: #252540; }

    .refresh-info {
      text-align: center; margin-top: 20px;
      color: #5050708; font-size: 0.82rem; color: #505070;
    }
  </style>
</head>
<body>

<nav>
  <div class="nav-brand">🚨 City Rescue Simulator</div>
  <ul class="nav-links">
    <li><a href="index.html">← Zpět na web</a></li>
    <li><a href="zebricek.php" class="nav-btn">🏆 Žebříček</a></li>
  </ul>
</nav>

<div class="zebricek-hero">
  <h1>🏆 Nejlepší záchranáři</h1>
  <p>Top 20 hráčů City Rescue Simulator</p>
</div>

<div class="zebricek-wrap">
  <a href="index.html" class="zpet-btn">← Zpět na hlavní stránku</a>

  <?php if ($chyba): ?>
    <div class="chyba-box">
      ⚠️ <?= htmlspecialchars($chyba) ?>
    </div>
  <?php endif; ?>

  <?php if (empty($radky) && !$chyba): ?>
    <div class="prazdny">
      Zatím žádná skóre. Zahraj si hru a buď první! 🎮
    </div>
  <?php else: ?>
  <table class="score-table">
    <thead>
      <tr>
        <th class="rank">#</th>
        <th>Hráč</th>
        <th>Skóre</th>
        <th>Datum</th>
      </tr>
    </thead>
    <tbody>
      <?php foreach ($radky as $i => $r):
        $poradi = $i + 1;
        $rankClass = match($poradi) { 1 => 'rank-1', 2 => 'rank-2', 3 => 'rank-3', default => '' };
        $medal = match($poradi) { 1 => '🥇', 2 => '🥈', 3 => '🥉', default => $poradi };
      ?>
      <tr>
        <td class="rank <?= $rankClass ?>"><?= $medal ?></td>
        <td><?= htmlspecialchars($r['hrac']) ?></td>
        <td class="score-val"><?= (int)$r['body'] ?></td>
        <td class="datum-val">
          <?= htmlspecialchars(substr($r['datum'] ?? '', 0, 10)) ?>
        </td>
      </tr>
      <?php endforeach; ?>
    </tbody>
  </table>
  <p class="refresh-info">Aktualizováno: <?= date('H:i:s') ?></p>
  <?php endif; ?>
</div>

</body>
</html>
