

displayView = function(){
    // the code required to display a view
};
window.onload = function(){
    //code that is executed as the page is loaded.
    //You shall put your own custom code here.
    //window.alert() is not allowed to be used in your implementation.
    //window.alert("Hello TDDD97!");

    if (localStorage['currToken'] == null) {
      document.getElementById('currentView').innerHTML = document.getElementById('welcomeview').innerHTML;
      localStorage['currView'] = 'welcomeview';
      $(document).ready(function(){
        $("#loginSliderDiv").hide();
        $("#loginheaderbutton").click(function () {
          $("#loginSliderDiv").animate({width:'toggle'}, 300);
        });
        $("#signupheaderbutton").click(function () {
          $("#loginSliderDiv").animate({width:'toggle'}, 300);
        });
        $("#welcomeLoginButton").click(function () {
          $("#loginSliderDiv").animate({width:'toggle'}, 300);
        });
        $(".welcomeContainerButton").click(function () {
          $("#loginSliderDiv").animate({width:'toggle'}, 300);
        });
      });
    }
    else {
      SocketSetup();
      if (localStorage['currView'] == 'homeview'){
        homeClicked();
      }
      else if (localStorage['currView'] == 'accountview'){
        accountClicked();
      }
      else if (localStorage['currView'] == 'browseview'){
        browseClicked();
      }
    }

};

encryptData = function(data) {
  var hash = CryptoJS.HmacSHA256(data, localStorage['currToken']);
  var hashInBase64 = CryptoJS.enc.Base64.stringify(hash);
  return hashInBase64;
}

ChangePasswordClicked = function(form) {
  var currPassword = form.elements["currPassword"].value;
  var newPassword = form.elements["newPassword"].value;
  var repNewPassword = form.elements["repNewPassword"].value;
  if (repNewPassword === newPassword) {
    var post = new XMLHttpRequest();
    post.onreadystatechange=function() {
      if (post.readyState==4 && post.status==200){
          var response = JSON.parse(post.responseText);
          document.getElementById('changePasswordMessageBox').innerHTML = response.message;
          if(document.getElementById) {
              document.changePassForm.reset();
            }
      }
    }
    var formData = new FormData();
    formData.append('email', localStorage['currEmail']);
    formData.append('oldpassword', currPassword);
    formData.append('newpassword', newPassword);
    formData.append('blob', currPassword+newPassword);
    PostToServerSecure(post, "/changePassword", formData);
    //PostToServer(post, "/changePassword", "token=" + localStorage['currToken'] + "&oldpassword=" + currPassword + "&newpassword=" + newPassword);
  }
  else {
    document.getElementById('changePasswordMessageBox').innerHTML = "Please repeat the new password.";
  }
}

UserProfileData = function() {
  var post = new XMLHttpRequest();
  post.onreadystatechange=function() {
    if (post.readyState==4 && post.status==200){
        var response = JSON.parse(post.responseText);
      if(response.success) {
        document.getElementById('email').innerHTML = response.data.email;
        document.getElementById('firstName').innerHTML = response.data.firstname;
        document.getElementById('familyName').innerHTML = response.data.familyname;
        document.getElementById('gender').innerHTML = response.data.gender;
        document.getElementById('city').innerHTML = response.data.city;
        document.getElementById('country').innerHTML = response.data.country;
        var useremail = response.data.email;
        setUserProfileDataPic('homeProfilePicDiv', useremail);
      }
      else {
        console.log(response.message);
      }
    }
  }
  var formData = new FormData();
  formData.append('email', localStorage['currEmail']);
  formData.append('blob', localStorage['currEmail']);
  PostToServerSecure(post, "/getUserDataByToken", formData);
}

setUserProfileDataPic = function(divID, email){
  var post = new XMLHttpRequest();
  post.onreadystatechange=function() {
    if (post.readyState==4 && post.status==200){
        var response = JSON.parse(post.responseText);
      if(response.success) {
        //window.location.reload(true);
        document.getElementById(divID).innerHTML = '<img src="' + response.data + '" height="200" width="200">';
        return false;
      }
    }
  }
  var formData = new FormData();
  formData.append('email', localStorage['currEmail']);
  formData.append('userEmail', email);
  formData.append('blob', email);
  PostToServerSecure(post, "/getHomeProfilePic", formData);
}


PostToServer = function(req,route, data) {
  req.open('POST', route, true);
  req.setRequestHeader("Content-type","application/x-www-form-urlencoded");
  req.send(data);
}

SignInClicked = function(form) {
  var loginEmail = form.elements["loginEmail"].value;
  var loginPassword = form.elements["loginPassword"].value;
  var post = new XMLHttpRequest();
  post.onreadystatechange=function() {
	  if (post.readyState==4 && post.status==200){
		    var response = JSON.parse(post.responseText);
			if(response.success == true) {
        localStorage['currToken'] = response.data;
        localStorage['currEmail'] = loginEmail;
        SocketSetup();
        homeClicked();
			}
      else {
        document.getElementById('signinErrorBox').innerHTML = response.message;
			}
	  }
	}
  PostToServer(post, "/sign_in", "email=" + loginEmail + "&password=" + loginPassword);
}

SocketSetup = function() {
  webSocket = new WebSocket("ws://" + document.domain + ":5000/SocketSetup");

  webSocket.onopen = function() {
    var data = {"token": localStorage['currToken']};
    webSocket.send(JSON.stringify(data));
  }

  webSocket.onmessage = function(data) {
    message = JSON.parse(data.data);
    if (message.success == false) {
      Swal.fire(
        'Logged out!',
        'You have been automatically logged out!'
      )
      localStorage.removeItem('currToken');
      localStorage.removeItem('currEmail');
      document.getElementById('currentView').innerHTML = document.getElementById('welcomeview').innerHTML;
      localStorage['currView'] = 'welcomeview';
    }
    else if (message.message == "Update chart" && localStorage['currView'] == 'accountview') {
        renderStats();
      }
  }
}

SignUpClicked = function(form) {
  var regEmail = form.elements["regEmail"].value;
  var regPassword = form.elements["regPassword"].value;
  var regRepPassword = form.elements["regRepPassword"].value;
  var regFirstname = form.elements["regFirstname"].value;
  var regLastname = form.elements["regLastname"].value;
  var regCity = form.elements["regCity"].value;
  var regCountry = form.elements["regCountry"].value;
  var regSex = form.elements["regSex"].value;

  if (regPassword == regRepPassword) {
    var post = new XMLHttpRequest();
    post.onreadystatechange=function() {
      if (post.readyState==4 && post.status==200){
          var response = JSON.parse(post.responseText);
          if(response.success) {
            Swal.fire(
              'Account Created!',
              'You have successfully created an account',
              'success'
            )
            if(document.getElementById) {
                document.signupForm.reset();
              }
            document.getElementById('signupErrorBox').innerHTML = response.message;
            return false;
      		}
          else {
            Swal.fire(
              'Something went wrong!',
              response.message,
              'error'
            )
            document.getElementById('signupErrorBox').innerHTML = response.message;
            return false;
          }
      }
    }
    PostToServer(post, "/sign_up", "email=" + regEmail + "&password=" + regPassword + "&firstname=" + regFirstname  + "&familyname=" + regLastname  + "&gender=" + regSex  + "&city=" + regCity + "&country=" + regCountry);
  }
  else {
    document.getElementById('signupErrorBox').innerHTML = "Passwords do not match";
    return false;
  }
}

uploadProfileButtonClicked = function(form) {
  var fileInput = document.getElementById('fileToUpload');
  if(fileInput.files[0] === undefined) {
    document.getElementById('uploadProfileMessageBox').innerHTML = 'Please choose a image you want to upload.';
   }
   else {
      document.getElementById('profilePicDiv').innerHTML = "";
      var post = new XMLHttpRequest();
      post.onreadystatechange=function() {
        if (post.readyState==4 && post.status==200){
            var response = JSON.parse(post.responseText);
            document.getElementById('uploadProfileMessageBox').innerHTML = response.message;
          if(response.success) {
            document.getElementById('profilePicDiv').innerHTML = '<img src="' + response.data + '" height="200" width="200">';
          }
        }
      }

      var formData = new FormData();
      var fileInput = document.getElementById('fileToUpload');
      var file = fileInput.files[0];
      formData.append('file', file);
      formData.append('email', localStorage['currEmail']);
      formData.append('blob', localStorage['currEmail']);
      PostToServerSecure(post, "/setProfilePic", formData);
    }
}

logoutClicked = function() {
  var post = new XMLHttpRequest();
  post.onreadystatechange=function() {
    if (post.readyState==4 && post.status==200){
        var response = JSON.parse(post.responseText);
      if(response.success) {
        localStorage.removeItem('currToken');
        localStorage.removeItem('currEmail');
        document.getElementById('currentView').innerHTML = document.getElementById('welcomeview').innerHTML;
        localStorage['currView'] = 'welcomeview';
        Swal.fire(
          'Logged out!',
          'You have been logged out',
          'success'
        )
        return false;
      }
      else {
        console.log(resonse.message);
      }
    }
  }
  Swal.fire({
  title: 'Log out',
  text: "Are you sure you want to log out?",
  type: 'warning',
  showCancelButton: true,
  confirmButtonColor: '#00ca69',
  cancelButtonColor: '#d33',
  confirmButtonText: 'Yes, log me out'
  }).then((result) => {
    if (result.value) {
      var formData = new FormData();
      formData.append('email', localStorage['currEmail']);
      formData.append('blob', localStorage['currEmail']);
      PostToServerSecure(post, "/signOut", formData);
      return false;
    }
  })

}

browseClicked = function() {
  document.getElementById('currentView').innerHTML = document.getElementById('browseview').innerHTML;
  localStorage['currView'] = 'browseview';
}

accountClicked = function() {
  document.getElementById('currentView').innerHTML = document.getElementById('accountview').innerHTML;
  localStorage['currView'] = 'accountview';
  var post = new XMLHttpRequest();
  post.onreadystatechange=function() {
    if (post.readyState==4 && post.status==200){
        var response = JSON.parse(post.responseText);
      if(response.success) {
        document.getElementById('profilePicDiv').innerHTML = '<img src="' + response.data + '" height="200" width="200">';
        renderStats();
        return false;
      }
    }
  }
  var formData = new FormData();
  formData.append('email', localStorage['currEmail']);
  formData.append('userEmail', localStorage['currEmail']);
  formData.append('blob', localStorage['currEmail']);
  PostToServerSecure(post, "/getHomeProfilePic", formData);
}

renderStats = function() {
  var post = new XMLHttpRequest();
  post.onreadystatechange=function() {
    if (post.readyState==4 && post.status==200){
        var response = JSON.parse(post.responseText);
      if(response.success) {
        var dougChart = new Chart(document.getElementById("dougChart"), {
              type: 'doughnut',
              data: {
                labels: ["Total posts by you", "Posts by you on your wall", "Posts by other users on your wall"],
                datasets: [
                  {
                    label: "Population (millions)",
                    backgroundColor: ["#3e95cd", "#8e5ea2", "#2e53a2"],
                    data: [response.data.totalPostsByMe ,response.data.postsByMeOnMyWall, response.data.PostByOthersOnMyWall]
                  }
                ]
              },
              options: {
                responsive: true,
                maintainAspectRatio: false,
                title: {
                  display: true,
                  text: 'Post Statistics'
                }
              }
          });
        return false;
      }
    }
  }
  var formData = new FormData();
  formData.append('email', localStorage['currEmail']);
  formData.append('blob', localStorage['currEmail']);
  PostToServerSecure(post, "/getStats", formData);
}

BrowseButtonClicked = function(form) {
  var searchUser = form.elements["browseSearchUser"].value;
  var post = new XMLHttpRequest();
  post.onreadystatechange=function() {
    if (post.readyState==4 && post.status==200){
        var response = JSON.parse(post.responseText);
      if(response.success) {
        document.getElementById('currentView').innerHTML = document.getElementById('browsehomeview').innerHTML;
        //localStorage['currView'] = 'browsehomeview';
        document.getElementById('browseEmail').innerHTML = response.data.email;
        document.getElementById('browseFirstName').innerHTML = response.data.firstname;
        document.getElementById('browseFamilyName').innerHTML = response.data.familyname;
        document.getElementById('browseGender').innerHTML = response.data.gender;
        document.getElementById('browseCity').innerHTML = response.data.city;
        document.getElementById('browseCountry').innerHTML = response.data.country;
        var useremail = response.data.email;
        setUserProfileDataPic('browseHomeProfilePicDiv', useremail);
        browseLoadOldMessages();
      }
      else {
        Swal.fire(
          response.message,
          'error'
        )
      }
    }
  }
  var formData = new FormData();
  formData.append('email', localStorage['currEmail']);
  formData.append('searchUser', searchUser);
  formData.append('blob', searchUser);
  PostToServerSecure(post, "/getUserDataByEmail", formData);
}

homeClicked = function() {
  UserProfileData(); //kanske returna true eller false
  loadOldMessages();
  document.getElementById('currentView').innerHTML = document.getElementById('homeview').innerHTML;
  localStorage['currView'] = 'homeview';
  return;
}

retrieveUserDataToken = function(token) {
  var post = new XMLHttpRequest();
  post.onreadystatechange=function() {
    if (post.readyState==4 && post.status==200){
        var response = JSON.parse(post.responseText);
      if(response.success) {
        var email = response.data.email;
        return email;
      }
      else {
        return response.data;
      }
    }
    else {
      return "null";
    }
  }
  var formData = new FormData();
  formData.append('email', localStorage['currEmail']);
  formData.append('blob', localStorage['currEmail']);
  PostToServerSecure(post, "/getUserDataByToken", formData);
}

postMessageClicked = function(form) {
  var message = form.elements["message"].value;
  var post = new XMLHttpRequest();
  post.onreadystatechange=function() {
    if (post.readyState==4 && post.status==200){
        var response = JSON.parse(post.responseText);
      if(response.success) {
        var email = response.data.email;
        var post2 = new XMLHttpRequest();
        post2.onreadystatechange=function() {
          if (post2.readyState==4 && post2.status==200){
              var response = JSON.parse(post2.responseText);
            if(response.success) {
              loadOldMessages();
              return false;
            }
            else {
              document.getElementById('postErrorBox').innerHTML = response.message;
            }
          }
        }
        var formData = new FormData();
        formData.append('message', message);
        formData.append('email', localStorage['currEmail']);
        formData.append('toEmail', email);
        formData.append('blob', message+email);
        PostToServerSecure(post2, "/postMessage", formData);
        //PostToServer(post2, "/postMessage", "token=" + localStorage['currToken'] + "&message=" + message +"&email=" + email + "&hash=" + hash);
      }
    }
    //return false;
  }
  var formData = new FormData();
  formData.append('email', localStorage['currEmail']);
  formData.append('blob', localStorage['currEmail']);
  PostToServerSecure(post, "/getUserDataByToken", formData);
  document.getElementById('postMessageText').value = "";
  return false;
}

PostToServerSecure = function(req, route, formData) {
  hash = encryptData(formData.get('blob'));
  formData.append('hash', hash);
  req.open('POST', route, true);
  req.send(formData);
}

browsePostMessageClicked = function(form) {
  var message = form.elements["message"].value;
  var email = document.getElementById('browseEmail').innerHTML;
  var post2 = new XMLHttpRequest();
  post2.onreadystatechange=function() {
    if (post2.readyState==4 && post2.status==200){
        var response = JSON.parse(post2.responseText);
      if(response.success) {
        browseLoadOldMessages();
        return false;
      }
      else {
        document.getElementById('postErrorBox').innerHTML = response.message;
      }
    }
  }
  var formData = new FormData();
  formData.append('message', message);
  formData.append('email', localStorage['currEmail']);
  formData.append('toEmail', email);
  formData.append('blob', message+email);
  PostToServerSecure(post2, "/postMessage", formData);
  document.getElementById('browsePostMessageText').value = "";
  return false;
}


loadOldMessages = function() {
  var post = new XMLHttpRequest();
  post.onreadystatechange=function() {
    if (post.readyState==4 && post.status==200){
      var response = JSON.parse(post.responseText);
      if(response.success) {
        document.getElementById('messageArea').innerHTML = "";
        var ul = document.getElementById('messageArea');
        for (var i = 0; i < response.data.length; i++) {
          var li = document.createElement('li');
          //li.appendChild(document.createTextNode(response.data[i].writer + ': ' + response.data[i].content));

          picSrc = "static/profilepics/" + response.data[i].profilepic;
          var image = document.createElement("img");
          image.src = picSrc;
          image.style.width = "40px";
          image.style.height = "40px";
          image.style.marginTop = "7px";
          li.appendChild(image);
          li.innerHTML += response.data[i].writer + '<br />' + response.data[i].content;
          ul.appendChild(li);
          //document.getElementsByClassName(response.data[i].writer).src = picSrc;

        }
        return;
      }
      else {
        return false;
      }
    }
  }
  var formData = new FormData();
  formData.append('email', localStorage['currEmail']);
  formData.append('blob', localStorage['currEmail']);
  PostToServerSecure(post, "/getUserMessagesByToken", formData);
}

browseLoadOldMessages = function() {
  var email = document.getElementById('browseEmail').innerHTML;
  var post = new XMLHttpRequest();
  post.onreadystatechange=function() {
    if (post.readyState==4 && post.status==200){
        var response = JSON.parse(post.responseText);
        if(response.success) {
          document.getElementById('browseMessageArea').innerHTML = "";
          var ul = document.getElementById('browseMessageArea');
          for (var i = 0; i < response.data.length; i++) {
            var li = document.createElement('li');
            picSrc = "static/profilepics/" + response.data[i].profilepic;
            var image = document.createElement("img");
            image.src = picSrc;
            image.style.width = "40px";
            image.style.height = "40px";
            image.style.marginTop = "7px";
            li.appendChild(image);
              li.innerHTML += response.data[i].writer + '<br />' + response.data[i].content;
            ul.appendChild(li);
            //document.getElementsByClassName(response.data[i].writer).src = picSrc;

          }
          return;
        }
        else {
          return false;
        }
    }
  }
  var formData = new FormData();
  formData.append('email', localStorage['currEmail']);
  formData.append('fromEmail', email);
  formData.append('blob', email);
  PostToServerSecure(post, "/getUserMessagesByEmail", formData);
}

welcomeContainerVideoButtonClicked = function() {
  swal.fire({
    background: 'rgb(0,0,0,0)',
    html: '<iframe width="100%" height="500" src="static/test.mp4" frameborder="0"></iframe>',
    showCancelButton: false,
    showConfirmButton: false,
    showCloseButton: true
  });
}
