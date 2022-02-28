var device;
var userName;

function handleAddDevice(e){
  e.preventDefault();
  form = document.getElementById("addDeviceForm");
  deviceCode = form.elements["code"].value;
  console.log("Code: " + deviceCode)
  fetch('/addDevice', {
    method: "POST",
    headers: {'Content-Type': 'application/json; charset=UTF-8'},
    body: JSON.stringify({code: deviceCode})
  })
    .then(response => response.json())
    .then((data) => {
      device = data.device;
      if(device == null){
        alert("This device is already registered or the code you entered is invalid");
      } else {
        document.getElementById("device").innerHTML = "Device: " + device;
        document.getElementById("addDevice").style.display="none";
        document.getElementById("removeDevice").style.display="block";
        form.reset();
      }
    });
}

document.getElementById("addDeviceForm").addEventListener("submit", handleAddDevice);

function handleRemoveDevice(){
  fetch('/removeDevice', {
    method: "POST",
    headers: {'Content-Type': 'application/json; charset=UTF-8'},
    body: JSON.stringify({code: device})
  })
    .then(response => response.json())
    .then((data) => {
      if(data.success){
        device = null;
        document.getElementById("addDevice").style.display="block";
        document.getElementById("removeDevice").style.display="none";
      } else {
        alert("Unable to remove device - a session may be in progress");
      }
    })
}

document.getElementById("removeDeviceButton").addEventListener("click", handleRemoveDevice);

document.addEventListener("DOMContentLoaded", function () {
  fetch('/getUser')
    .then(response => response.json())
    .then((data) => {
      device = data.device;
      if(device==null) {
        document.getElementById("addDevice").style.display="block";
        document.getElementById("removeDevice").style.display="none";
      } else {
        document.getElementById("device").innerHTML = "Device: " + device;
        document.getElementById("addDevice").style.display="none";
        document.getElementById("removeDevice").style.display="block";
      }
      userName = data.name;
      document.getElementById("homeTitle").innerHTML = "Welcome, " + userName;
    });
});