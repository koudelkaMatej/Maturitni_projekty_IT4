<?php
ini_set('display_errors',1);
error_reporting(E_ALL);

$conn = new mysqli(
    "dbs.spskladno.cz",
    "student31",
    "spsnet",
    "vyuka31"
);

if($conn->connect_error){
    die("DB error");
}

$players = $conn->query("
    SELECT username, highscore
    FROM users
    ORDER BY highscore DESC
");
?>
<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="UTF-8">
<title>Goblin Invasion – Leaderboard</title>

<style>

body{
    background:#0b3d2e;
    color:white;
    font-family:Arial;
    text-align:center;
}

h1{color:gold;}

#controls{
    margin:15px;
}

button{
    padding:6px 12px;
    margin:5px;
    cursor:pointer;
}

table{
    margin:auto;
    border-collapse:collapse;
    width:500px;
}

th,td{
    padding:10px;
    border:1px solid white;
}

th{
    cursor:pointer;
    background:#145a45;
}

tr:hover{
    background:#1b6b54;
}

.highlight{
    background:#ffd70055;
}

#detail{
    margin-top:20px;
    font-size:18px;
    min-height:40px;
}

</style>
</head>

<body>

<h1>🏹 Goblin Invasion</h1>

<div id="controls">

<button onclick="showTop()">TOP 10</button>
<button onclick="showAll()">Všichni</button>

<input id="search" placeholder="Hledej hráče" onkeyup="filter()">

</div>


<table id="table">

<tr>
<th onclick="sortTable(0)">#</th>
<th onclick="sortTable(1)">Jméno</th>
<th onclick="sortTable(2)">Skóre</th>
</tr>

<?php
$i=1;
while($p=$players->fetch_assoc()){

    echo "<tr onclick=\"detail(this)\">";
    echo "<td>$i</td>";
    echo "<td>{$p['username']}</td>";
    echo "<td>{$p['highscore']}</td>";
    echo "</tr>";

    $i++;
}
?>

</table>


<div id="detail"></div>


<script>

let table = document.getElementById("table");
let rows = Array.from(table.rows).slice(1);


// Filtrování
function filter(){

    let text = document.getElementById("search").value.toLowerCase();

    rows.forEach(r=>{

        let name = r.cells[1].innerText.toLowerCase();

        r.style.display =
            name.includes(text) ? "" : "none";
    });
}


// Řazení
function sortTable(col){

    rows.sort((a,b)=>{

        let x=a.cells[col].innerText;
        let y=b.cells[col].innerText;

        if(col==2) return y-x;

        return x.localeCompare(y);
    });

    rows.forEach(r=>table.appendChild(r));
}


// TOP 10
function showTop(){

    rows.forEach((r,i)=>{

        r.style.display = i<10 ? "" : "none";
    });
}


// All
function showAll(){

    rows.forEach(r=>r.style.display="");
}


// Detail hráče
function detail(row){

    rows.forEach(r=>r.classList.remove("highlight"));

    row.classList.add("highlight");

    let name=row.cells[1].innerText;
    let score=row.cells[2].innerText;

    document.getElementById("detail").innerHTML=
        "Hráč: <b>"+name+"</b> | Skóre: <b>"+score+"</b>";
}

</script>

</body>
</html>
