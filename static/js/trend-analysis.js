var trigger = document.getElementById("timerange-selector");
var target = document.getElementById("customizedtime-div");
var fromDate = document.getElementById("from-date");
var toDate = document.getElementById("to-date");
var step1_triggers = document.querySelectorAll(".step1-trigger");
var step2_triggers = document.querySelectorAll(".step2-trigger");
var step3_triggers = document.querySelectorAll(".step3-trigger");

function timeErrorMessage() {
    var inputError = document.getElementById("inputError")
    if (trigger.value == "customized-time"){
        if ((fromDate.value=="") || (toDate.value==""))
        {
            inputError.innerHTML = "<span style='color: #f55c47;'>"+
                        "Please complete your customized time range.</span>"
            return false
        } else if ((Date.parse(toDate.value) < Date.parse(fromDate.value))) {
            inputError.innerHTML = "<span style='color: #f55c47;'>"+
                        "Start date cannot be greater than end date.</span>"
            toDate.value = ""
            return false
        } else {
            inputError.innerHTML = ""
            return true
        }
    }  
};

trigger.addEventListener("change", function () {
    if (this[this.selectedIndex].value === "customized-time") {
        target.classList.add("show");
    } else {
        target.classList.remove("show");
    }
}, false);


function openTab(evt, tabName) {
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
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
};



step1_triggers.forEach(item => {
    item.addEventListener('click', event => {
        document.getElementById("step1-btn").click();
    })
});

step2_triggers.forEach(item => {
    item.addEventListener('click', event => {
        document.getElementById("step2-btn").click();
    })
});

step3_triggers.forEach(item => {
    item.addEventListener('click', event => {
        document.getElementById("step3-btn").click();
    })
});