function challengeMatch(e) {
  fetch('/postmatch', {
    method : 'POST',
    body : JSON.stringify({
      'ladder_id' : document.getElementById('ladder_id').value,
      // 'team-1' : document.getElementById('team-1').value,
      'team-1-id' : document.getElementById('team-1-id').value,
      'team-2' : document.getElementById('team-2').value,
      'best' : document.getElementById('best').value,
      'datetime' : document.getElementById('datetime').value,
      'players' : document.getElementById('players').value,
      'member-count' : document.getElementById('member-count').value,
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.status == "success") {
      location.reload();
    }
    msg = document.querySelector("#msg_frm")

    msg.innerHTML = `<div class="alert alert-danger" role="alert">
                    <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                    <strong>${data.message}!</strong> 
                    </div>`
        })
    // e.preventDefault()
}

function openTab(evt, cityName) {
    // Declare all variables
    var i, tabcontent, tablinks;
  
    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }
  
    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
  
    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(cityName).style.display = "block";
    evt.currentTarget.className += " active";
  }
document.getElementById("defaultOpen").click();

