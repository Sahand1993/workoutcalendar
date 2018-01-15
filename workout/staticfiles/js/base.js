//logoutbutton
logoutbutton = document.getElementById("logoutbutton");

if(logoutbutton){
    logoutbutton.onclick = logout;
}

function logout(){
    window.location = "/workoutcal/logout";
}

//loginbutton
loginbutton = document.getElementById("loginbutton");

if(loginbutton){
    loginbutton.onclick = login;
}

function login(){
    window.location = "/workoutcal/login";
}