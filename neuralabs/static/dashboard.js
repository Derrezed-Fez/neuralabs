var randomScalingFactor = function() {
  return Math.round(Math.random() * 100);
};

var color = Chart.helpers.color;
var config = {
  type: 'radar',
  data: {
    labels: [['Digital Forensics', 'Network Forensics'], ['Ethical Hacking', 'Server Hardening'], 'Automotive Security', ['Incident Response', 'Social Engineering'], 'Malware', 'Reverse Engineering', 'CodeOps'],
    datasets: [{
      label: 'My First dataset',
      backgroundColor: 'red',
      borderColor: 'red',
      pointBackgroundColor: 'red',
      data: [
        randomScalingFactor(),
        randomScalingFactor(),
        randomScalingFactor(),
        randomScalingFactor(),
        randomScalingFactor(),
        randomScalingFactor(),
        randomScalingFactor()
      ]
    }, {
      label: 'My Second dataset',
      backgroundColor: 'blue',
      borderColor: 'blue',
      pointBackgroundColor: 'blue',
      data: [
        randomScalingFactor(),
        randomScalingFactor(),
        randomScalingFactor(),
        randomScalingFactor(),
        randomScalingFactor(),
        randomScalingFactor(),
        randomScalingFactor()
      ]
    }]
  },
  options: {
    legend: {
      position: 'top',
    },
    title: {
      display: true,
      text: 'Lab Distribution'
    },
    scale: {
      beginAtZero: true
    },
    responsive: false
  }
};

window.onload = function() {
  window.myRadar = new Chart(document.getElementById('stats'), config);
};
