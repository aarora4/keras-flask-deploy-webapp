//========================================================================
// Drag and drop image handling
//========================================================================

var fileDrag = document.getElementById("file-drag");
var fileSelect = document.getElementById("file-upload");

// Add event listeners
fileDrag.addEventListener("dragover", fileDragHover, false);
fileDrag.addEventListener("dragleave", fileDragHover, false);
fileDrag.addEventListener("drop", fileSelectHandler, false);
fileSelect.addEventListener("change", fileSelectHandler, false);


function fileDragHover(e) {
  // prevent default behaviour
  e.preventDefault();
  e.stopPropagation();

  fileDrag.className = e.type === "dragover" ? "upload-box dragover" : "upload-box";
}

function fileSelectHandler(e) {
  // handle file selecting
  var files = e.target.files || e.dataTransfer.files;
  fileDragHover(e);
  for (var i = 0, f; (f = files[i]); i++) {
    previewFile(f);
  }
}

//========================================================================
// Web page elements for functions to use
//========================================================================
var willHeText = document.getElementById("willhetext");
var fileSuccess = document.getElementById("was-success");
var forthissong = document.getElementById("forthissong");
var justopinion = document.getElementById("justopinion");
var spinner = document.getElementById("spinner")
var imagePreview = document.getElementById("image-preview");
var imageDisplay = document.getElementById("image-display");
var uploadCaption = document.getElementById("upload-caption");
var predResult = document.getElementById("pred-result");
// var loader = document.getElementById("loader");

//========================================================================
// Main button events
//========================================================================

function submitImage() {
  // action for the submit button
  console.log("submit");

  // call the predict function of the backend
  

  if (globFile !== null) {
    if (globFile.type.split('/')[0] == 'audio') {
      hide(fileSuccess)
      show(spinner)
      predictImage(globFile);
    } else {
      window.alert("Invalid File Type. Please submit an audio file");
    }
  } else {
    window.alert("Please upload a .wav file before submitting");
  }

}

function clearImage() {
  // reset selected files
  fileSelect.value = "";

  // remove image sources and hide them
  imagePreview.src = "";
  imageDisplay.src = "";
  predResult.innerHTML = "";

  globFile = null

  hide(imagePreview);
  hide(imageDisplay);
  // hide(loader);
  hide(predResult);
  show(uploadCaption);
  show(willhetext)
  hide(justopinion)
  hide(forthissong)

  

  imageDisplay.classList.remove("loading");
}

function previewFile(file) {
  // show the preview of the image
  console.log(file)
  globFile = file;
  console.log(file.name);
  var fileName = encodeURI(file.name);
  // console.log()
  var reader = new FileReader();
  imagePreview.innerText = fileName;
  show(imagePreview);
  hide(uploadCaption);
  show(fileSuccess)
  hide(willhetext)

}
var globFile = null;

//========================================================================
// Helper functions
//========================================================================

function predictImage(image) {
  // console.log(image.blob)
  var form = new FormData();
  form.append('audio_file', image, "poopy.wav")
  // "Content-Type": "multipart/form-data"
  fetch("/predict", {
    method: "POST",
    headers: {
    },
    body: form
  })
    .then(resp => {
      if (resp.ok)
        resp.json().then(response => {
          // displayResult(data);
          // console.log(data)
          get_status(response.data.taskID, displayResult);

        });
    })
    .catch(err => {
      console.log("An error occured", err.message);
      window.alert("Oops! Something went wrong.");
    });
}

function displayImage(image, id) {
  // display image on given id <img> element
  let display = document.getElementById(id);
  display.src = image;
  show(display);
}

function displayResult(data, errors) {
  // display the result
  // imageDisplay.classList.remove("loading");
  // hide(loader);
  // predResult.innerHTML = data.result;
  // show(predResult);

  hide(spinner)

  imageDisplay.src = './static/' + String(data[0]) + '.png'

  if (imageDisplay.classList.contains('hidden')) {
    show(imageDisplay)
  }
  
  show(justopinion)
  show(forthissong)
  
}

function get_status(taskID, funcToCall) {
  $.ajax({
      method: 'GET',
      url: `tasks/${taskID}`
  })
      .done((response) => {
          const taskStatus = response.data.taskStatus;

          if (taskStatus === 'failed') {
              console.log(response);
              return false;
          }
          else if (taskStatus == 'finished') {
              // Parse the returned JSON and return the link to the image.
              console.log(response);

              funcToCall(response.data.taskResult.result, response.data.taskResult.errors);
              return false;
          }

          // If the task hasn't been finished, try again in 1 second.
          setTimeout(function () {
              get_status(response.data.taskID, funcToCall);
          }, 1000);
      })
      .fail((error) => {
          console.log(error);
      });
}

function hide(el) {
  // hide an element
  el.classList.add("hidden");
}

function show(el) {
  // show an element
  el.classList.remove("hidden");
}