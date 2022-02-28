var colourData = [];
var intensity = 0;
var tempData = [];
var humidityData = [];
var tempDataSession = [];
var humidityDataSession = [];
var scoreData = [];

var minTemp = 0;
var maxTemp = 0;
var minHumid = 0;
var maxHumid = 0;

var minTempSession = 0;
var maxTempSession = 0;
var minHumidSession = 0;
var maxHumidSession = 0;

var minScore = 0;
var maxScore = 0;

var colourChart;
var tempHumidChart;
var tempHumidSessionChart;
var scoreChart;

var ccRendered = false;
var thcRendered = false;
var thscRendered = false;
var scRendered = false;

var colourChartOptions = {
series: colourData,
chart: {
  type: 'radialBar',
},
title: {
  text: "Light Intensity and Colour Spectrum",
  align: 'center',
  style: {
    fontSize: '17px',
    fontWeight: 'normal',
  },
},
plotOptions: {
  radialBar: {
    dataLabels: {
      name: {
        fontSize: '22px',
        color: '#373d3f',
      },
      value: {
        fontSize: '16px',
      },
      total: {
        show: true,
        label: 'Intensity',
        formatter: function (w) {
          // By default this function returns the average of all series. The below is just an example to show the use of custom formatter function
          return intensity.toFixed(0)+" lux";
        }
      }
    }
  }
},
fill: {
  colors: ['#8F00FF','#0000FF','#00FF00','#FFFF00','#FFA500','#FF0000'],
},
labels: ['Violet', 'Blue', 'Green', 'Yellow', 'Orange', 'Red'],
};

var tempHumidChartOptions = {
series: [{
  name: "Temperature",
  data: tempData
},{
  name: "Humidity",
  data: humidityData
}],
chart: {
  type: 'line',
  zoom: {
    enabled: false
  }
},
dataLabels: {
  enabled: false
},
stroke: {
  curve: 'smooth'
},
title: {
  align: 'center',
  style: {
    fontSize: '17px',
    fontWeight: 'normal',
  },
  text: 'Atmospheric Conditions this Session'
},
grid: {
  row: {
    colors: ['#f3f3f3', 'transparent'], // takes an array which will be repeated on columns
    opacity: 0.5
  },
},
xaxis: {
  type:'datetime',
  title: {
    text: "Time",
    style: {
      fontWeight: 'normal'
    }
  },
  labels: {
    format: "HH:mm"
  }
},
yaxis: [{
  forceNiceScale: true,
  min: function(){
    return minTemp;
  },
  max: function(){
    return maxTemp;
  },
  labels: {
    formatter: function (val) {
      return val.toFixed(1);
    }
  },
  title: {
    text: "Temperature (\u00B0C)",
    style: {
      fontWeight: 'normal'
    }
  }
},{
  opposite: true,
  forceNiceScale: true,
  min: function(){
    return minHumid;
  },
  max: function(){
    return maxHumid;
  },
  labels: {
    formatter: function(val) {
      return val.toFixed(1)
    },
  },
  title: {
    text: "Humidity (%)",
    style: {
      fontWeight: 'normal'
    }
  }
}],
tooltip: {
  shared: true,
  x: {
    format: "HH:mm"
  },
  y: [{
    formatter: function(val) {
      return val.toFixed(2) + "\u00B0C";
    }
  },{
    formatter: function(val) {
      return val.toFixed(2) + "%";
    }
  }]
}
};

var scoreChartOptions = {
  series: [{
    name: "Score",
    data: scoreData
  }],
  chart: {
    type: 'line',
    zoom: {
      enabled: false
    }
  },
  dataLabels: {
    enabled: false
  },
  stroke: {
    curve: 'smooth'
  },
  title: {
    align: 'center',
    style: {
      fontSize: '17px',
      fontWeight: 'normal',
    },
    text: 'Historic Session Scores'
  },
  grid: {
    row: {
      colors: ['#f3f3f3', 'transparent'], // takes an array which will be repeated on columns
      opacity: 0.5
    },
  },
  xaxis: {
    type:'datetime',
    title: {
      text: "Date / Time",
      style: {
        fontWeight: 'normal'
      }
    },
    labels: {
      format: "dd/MM HH:mm"
    }
  },
  yaxis: {
    forceNiceScale: true,
    min: function(){
      return minScore;
    },
    max: function(){
      return maxScore;
    },
    title: {
      text: "Score",
      style: {
        fontWeight: 'normal'
      }
    }
  },
  tooltip: {
    x: {
      format: "dd/MM HH:mm"
    },
  }
};

var tempHumidSessionChartOptions = {
series: [{
  name: "Temperature",
  data: tempDataSession
},{
  name: "Humidity",
  data: humidityDataSession
}],
chart: {
  type: 'line',
  zoom: {
    enabled: false
  }
},
dataLabels: {
  enabled: false
},
stroke: {
  curve: 'smooth'
},
title: {
  align: 'center',
  style: {
    fontSize: '17px',
    fontWeight: 'normal',
  },
  text: 'Historic Session Temperature and Humidity'
},
grid: {
  row: {
    colors: ['#f3f3f3', 'transparent'], // takes an array which will be repeated on columns
    opacity: 0.5
  },
},
xaxis: {
  type:'datetime',
  title: {
    text: "Date / Time",
    style: {
      fontWeight: 'normal'
    }
  },
  labels: {
    format: "dd/MM HH:mm"
  }
},
yaxis: [{
  forceNiceScale: true,
  min: function(){
    return minTempSession;
  },
  max: function(){
    return maxTempSession;
  },
  labels: {
    formatter: function (val) {
      return val.toFixed(1);
    }
  },
  title: {
    text: "Temperature (\u00B0C)",
    style: {
      fontWeight: 'normal'
    }
  }
},{
  opposite: true,
  forceNiceScale: true,
  min: function(){
    return minHumidSession;
  },
  max: function(){
    return maxHumidSession;
  },
  labels: {
    formatter: function(val) {
      return val.toFixed(1)
    },
  },
  title: {
    text: "Humidity (%)",
    style: {
      fontWeight: 'normal'
    }
  }
}],
tooltip: {
  shared: true,
  x: {
    format: "dd/MM HH:mm"
  },
  y: [{
    formatter: function(val) {
      return val.toFixed(2) + "\u00B0C";
    }
  },{
    formatter: function(val) {
      return val.toFixed(2) + "%";
    }
  }]
}
};



function LatestData() {
  fetch('/getLatestData')
    .then(response => response.json())
    .then((data) => {
      if(data.success){
        document.getElementById("temp").innerHTML = "Current temperature: "+data.temperature.toFixed(2)+"<span>&#176;</span>c";
        document.getElementById("humidity").innerText = "Current humidity: " + data.humidity.toFixed(2)+"%";
        intensity = data.intensity;
        colourData = data.colours;
        if(ccRendered) {
          colourChart.updateSeries(colourData, true);
        } else {
          colourChart = new ApexCharts(document.querySelector("#colourChart"), colourChartOptions);
          colourChart.render();
          colourChart.updateSeries(colourData, true);
          ccRendered = true;
        } 
      }
    });
}

function TempHumidityGraph() {
  fetch('/tempHumidityData')
    .then(response => response.json())
    .then((data) => {
      if(data.success){
        minHumid = data.minhumidity;
        minTemp = data.mintemp;
        maxHumid = data.maxhumidity;
        maxTemp = data.maxtemp;
        humidityData = data.humidity;
        tempData = data.temperature;
        if(thcRendered){
          tempHumidChart.updateSeries([{
            name: "Temperature",
            data: tempData
          },{
            name: "Humidity",
            data: humidityData
          }], true);
        } else {
          tempHumidChart = new ApexCharts(document.querySelector("#tempHumidChart"), tempHumidChartOptions);
          tempHumidChart.render();
          tempHumidChart.updateSeries([{
            name: "Temperature",
            data: tempData
          },{
            name: "Humidity",
            data: humidityData
          }], true);
          thcRendered = true;
        }
      }
    });
}

function HistoricSessions() {
  fetch('/sessionData')
    .then(response => response.json())
    .then((data) => {
      if(data.success){
        minHumidSession = data.minhumidity;
        minTempSession = data.mintemp;
        maxHumidSession = data.maxhumidity;
        maxTempSession = data.maxtemp;
        minScore = data.minscore;
        maxScore = data.maxscore
        humidityDataSession = data.humidity;
        tempDataSession = data.temperature;
        scoreData = data.score;
        if(thscRendered){
          tempHumidSessionChart.updateSeries([{
            name: "Temperature",
            data: tempDataSession
          },{
            name: "Humidity",
            data: humidityDataSession
          }], true);
        } else {
          tempHumidSessionChart = new ApexCharts(document.querySelector("#tempHumidSessionChart"), tempHumidSessionChartOptions);
          tempHumidSessionChart.render()
          tempHumidSessionChart.updateSeries([{
            name: "Temperature",
            data: tempDataSession
          },{
            name: "Humidity",
            data: humidityDataSession
          }], true);
          thscRendered = true;
        }
        if(scRendered){
          scoreChart.updateSeries([{
            name: "Score",
            data: scoreData
          }],true);
        } else {
          scoreChart = new ApexCharts(document.querySelector("#scoreChart"), scoreChartOptions);
          scoreChart.render();
          scoreChart.updateSeries([{
            name: "Score",
            data: scoreData
          }],true);
          scRendered = true;
        }
      }
    });
}

document.addEventListener("DOMContentLoaded", function () {
  LatestData();
  TempHumidityGraph();
  HistoricSessions();
});

setInterval(LatestData, 20000);
setInterval(TempHumidityGraph, 60000);