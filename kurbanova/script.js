const data = window.CATFORMER_LEADERBOARD || {
  leaderboard: [],
  summary: {}
};

const leaderboardBody = document.getElementById("leaderboard-body");
const updatedAt = document.getElementById("updated-at");
const totalPlayers = document.getElementById("total-players");
const finishedGames = document.getElementById("finished-games");
const bestScore = document.getElementById("best-score");
const topPlayer = document.getElementById("top-player");

function setText(node, value) {
  if (node) {
    node.textContent = value;
  }
}

function renderSummary(summary) {
  setText(totalPlayers, summary.total_players ?? 0);
  setText(finishedGames, summary.finished_games ?? 0);
  setText(bestScore, `${summary.best_score ?? 0} mincí`);

  if (summary.top_player) {
    setText(
      topPlayer,
      `${summary.top_player.username} | level ${summary.top_player.level} | ${summary.top_player.stars} minci`
    );
  } else {
    setText(topPlayer, "Zatím bez záznamu");
  }
}

function renderLeaderboard(rows) {
  if (!leaderboardBody) {
    return;
  }

  if (!rows.length) {
    leaderboardBody.innerHTML = `
      <tr>
        <td colspan="5" class="leaderboard__empty">
          Zatím tu nejsou uložené žádné výsledky. Spusť hru, dohraj level a web se po dalším otevření aktualizuje.
        </td>
      </tr>
    `;
    return;
  }

  leaderboardBody.innerHTML = rows
    .map(
      (entry, index) => `
        <tr>
          <td>${index + 1}.</td>
          <td>${entry.username}</td>
          <td>${entry.level}</td>
          <td>${entry.stars}</td>
          <td>${entry.date}</td>
        </tr>
      `
    )
    .join("");
}

renderSummary(data.summary || {});
renderLeaderboard(data.leaderboard || []);

if (data.generated_at) {
  setText(updatedAt, `Poslední aktualizace: ${data.generated_at.replace("T", " ")}`);
} else {
  setText(updatedAt, "Poslední aktualizace: zatím bez exportu");
}
