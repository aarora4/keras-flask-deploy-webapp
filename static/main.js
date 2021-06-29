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
console.log(fileSuccess);
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
    if (globFile.type == 'audio/wav') {
      hide(fileSuccess)
      show(spinner)
      predictImage(globFile);
    } else {
      window.alert("Invalid File Type. Please submit a .wav file");
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
        resp.json().then(data => {
          // displayResult(data);
          console.log(data.result[0]);
          hide(spinner)

          imageDisplay.src = './static/' + String(data.result[0]) + '.png'

          if (imageDisplay.classList.contains('hidden')) {
            show(imageDisplay)
          }
          
          show(justopinion)
          show(forthissong)

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

function displayResult(data) {
  // display the result
  // imageDisplay.classList.remove("loading");
  // hide(loader);
  predResult.innerHTML = data.result;
  show(predResult);
}

function hide(el) {
  // hide an element
  el.classList.add("hidden");
}

function show(el) {
  // show an element
  el.classList.remove("hidden");
}