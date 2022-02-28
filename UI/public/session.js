var sessionStarted = false;

document.addEventListener("DOMContentLoaded", function () {
  fetch('/sessionStatus')
    .then(response => response.json())
    .then((data) => {
      device = data.device;
      if(device==null) {
        document.getElementById("addDevice").style.display="block";
        document.getElementById("sessionStartStop").style.display="none";
      } else {
        document.getElementById("addDevice").style.display="none";
        document.getElementById("sessionStartStop").style.display="block";
        sessionStarted = data.sessionStarted;
        console.log("Session started? ",sessionStarted);
        if(!sessionStarted){
          document.getElementById("startStopText").innerHTML = "Start a session";
          document.getElementById("sessionButton").innerHTML = "Start";
        } else {
          document.getElementById("startStopText").innerHTML = "Stop a session";
          document.getElementById("sessionButton").innerHTML = "Stop";
        }
      }
    });
});

function handleSessionSubmission(e){
  e.preventDefault();
  form = document.getElementById("sessionForm");
  score = form.elements["sessionScore"].value;
  notes = form.elements["notes"].value;
  fetch('/stopSession', {
    method: "POST",
    headers: {'Content-Type': 'application/json; charset=UTF-8'},
    body: JSON.stringify({score: score, notes: notes})
  })
    .then(response => response.json())
    .then((data) => {
      if(data.success) {
        document.getElementById("startStopText").innerHTML = "Start a session";
        document.getElementById("sessionButton").innerHTML = "Start";
        sessionStarted = false;
        document.getElementById("sessionFormDiv").style.display="none";
        document.getElementById("sessionStartStop").style.display="block";
        form.reset();
      }
    });
}

function handleSessionStartStop(){
  if(sessionStarted){
    document.getElementById("sessionStartStop").style.display="none";
    document.getElementById("sessionFormDiv").style.display="block";
  } else {
    fetch('/startSession')
      .then(response => response.json())
      .then((data) => {
        if(data.success) {
          document.getElementById("startStopText").innerHTML = "Stop a session";
          document.getElementById("sessionButton").innerHTML = "Stop";
          sessionStarted = true;
        }
    });
  }
}

document.getElementById("sessionButton").addEventListener("click", handleSessionStartStop);
document.getElementById("sessionForm").addEventListener("submit", handleSessionSubmission);