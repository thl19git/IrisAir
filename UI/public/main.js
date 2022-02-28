navbar_height = document.querySelector('.navbar').offsetHeight;
document.body.style.paddingTop = navbar_height + 'px';

function checkForAlerts() {
  fetch('/getAlerts')
    .then(response => response.json())
    .then((data) => {
      if(data.alert){
        var toastElement = document.getElementById('alertToast');
        var toast = new bootstrap.Toast(toastElement);
        document.getElementById("AlertBody").innerHTML = data.message;
        toast.show();
      }
    });
}

setInterval(checkForAlerts, 30000);