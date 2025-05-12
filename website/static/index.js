function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}

document.addEventListener("DOMContentLoaded", function () {
  const chartElement = document.getElementById("expenseChart");
  const summaryElement = document.getElementById("summaryData");

  if (chartElement && summaryElement) {
    const ctx = chartElement.getContext("2d");
    const data = JSON.parse(summaryElement.textContent);
    const labels = Object.keys(data);
    const amounts = Object.values(data);
    const total = amounts.reduce((acc, val) => acc + val, 0);

    new Chart(ctx, {
      type: "pie",
      data: {
        labels: labels,
        datasets: [
          {
            data: amounts,
            backgroundColor: [
              "#FF6384",
              "#36A2EB",
              "#FFCE56",
              "#8BC34A",
              "#9C27B0",
              "#FF9800",
            ],
          },
        ],
      },
      options: {
        plugins: {
          tooltip: {
            callbacks: {
              label: function (context) {
                let label = context.label || "";
                let value = context.parsed || 0;
                let percent = ((value / total) * 100).toFixed(2);
                return `${label}: ₱${value} (${percent}%)`;
              },
            },
          },
          legend: {
            position: "bottom",
            labels: {
              boxWidth: 20,
              padding: 15,
            },
          },
        },
      },
    });
  }
});