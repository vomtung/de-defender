document.addEventListener("DOMContentLoaded", function () {
  fetch("/api/chart-data/")
    .then(response => response.json())
    .then(json => {
      const ctx = document.getElementById('myChart').getContext('2d');
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: json.labels,
          datasets: [{
            label: 'Requests per Month',
            data: json.data,
            backgroundColor: 'rgba(75, 192, 192, 0.6)',
            borderColor: 'teal',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
    });
});