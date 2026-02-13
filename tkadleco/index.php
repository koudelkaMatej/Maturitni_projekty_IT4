<?php
// index.php - Nahrajte do H:\public_html\
$host = "dbs.spskladno.cz"; // Na školním webu obvykle localhost
$db   = "vyuka14"; // Změňte na název vaší databáze
$user = "student14";     // Váš školní login
$pass = "spsnet";    // Vaše heslo k DB

// Připojení k databázi
try {
    $pdo = new PDO("mysql:host=$host;dbname=$db;charset=utf8", $user, $pass);
} catch (PDOException $e) {
    die("Chyba připojení: " . $e->getMessage());
}

// 1. ČÁST: Ukládání dat (komunikace s hrou)
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['hrac']) && isset($_POST['body'])) {
    $stmt = $pdo->prepare("INSERT INTO score_tabulka (hrac, body) VALUES (?, ?)");
    $stmt->execute([$_POST['hrac'], $_POST['body']]);
    echo "ULOZENO"; // Odpověď pro Python
    exit;
}

// 2. ČÁST: Webová stránka (zobrazení pro lidi)
$stmt = $pdo->query("SELECT * FROM score_tabulka ORDER BY body DESC LIMIT 10");
$radky = $stmt->fetchAll(PDO::FETCH_ASSOC);
?>

<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <title>Žebříček IZS Simulátoru</title>
    <style>
        body { font-family: sans-serif; background: #333; color: white; padding: 20px; }
        table { width: 100%; max-width: 600px; margin: 0 auto; border-collapse: collapse; background: #444; }
        th, td { padding: 10px; border: 1px solid #666; text-align: left; }
        th { background: #222; }
        h1 { text-align: center; color: #f0ad4e; }
    </style>
</head>
<body>
    <h1>🏆 Nejlepší záchranáři 🏆</h1>
    <table>
        <tr>
            <th>Jméno</th>
            <th>Skóre</th>
            <th>Datum</th>
        </tr>
        <?php foreach ($radky as $radek): ?>
        <tr>
            <td><?= htmlspecialchars($radek['hrac']) ?></td>
            <td><?= htmlspecialchars($radek['body']) ?></td>
            <td><?= htmlspecialchars($radek['datum']) ?></td>
        </tr>
        <?php endforeach; ?>
    </table>
</body>
</html>