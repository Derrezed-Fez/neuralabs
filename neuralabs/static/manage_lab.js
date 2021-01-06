function addLabPage() {
  var pageCount = $('.total-page-count').length;
  $('#total-page-count').val(pageCount);
  var page = `<div><div class="medium-6 cell"><label class="title-label">Page ${pageCount + 1} Title<input type="text" placeholder="Pre-Lab Setup"
  name="title-p${pageCount+1}"></label></div><div class="medium-6 cell"><label>Assignment Details<textarea style="height:100px;"
    placeholder="Step 1: boot up your VM..." name="details-p${pageCount+1}"></textarea></label></div><div class="medium-6 cell">
    <label>Scoring Engine Hash value&nbsp;<input type="checkbox" id="score_engine_enable_${pageCount+1}"><input type="text"
    placeholder="0xc0ffee" disabled id="score_engine_value_${pageCount+1}"/></label></div><div class="medium-6 cell">
    <label for="fileUpload1-p${pageCount + 1}" class="button">Upload External Media</label><input type="file"
    id="fileUpload1-p${pageCount + 1}" class="show-for-sr" name="fileUpload1-p${pageCount + 1}"
    onchange="displayUploadedFiles(this, 'files-p${pageCount + 1}');" /><input class="button" style="background-color:red; margin-left:5px;"
    onclick ="removeLabPage(event);" value="Remove Page"/></div><input type="hidden" class="total-page-count"/></div>`;
  document.getElementById('sequential_pages').insertAdjacentHTML("beforeend", page);

  $('#score_engine_enable_' + (pageCount + 1)).change(function() {
    var enabled = $('#score_engine_enable_' + (pageCount + 1)).is(':checked');
    if(enabled) {
      $('#score_engine_value_' + (pageCount + 1)).prop('disabled',false);
    } else {
      $('#score_engine_value_' + (pageCount + 1)).prop('disabled',true);
    }
  });
}

function removeLabPage(event) {
  event.currentTarget.parentNode.parentNode.parentNode.removeChild(event.currentTarget.parentNode.parentNode);
  $('#total-page-count').val($('.total_page_count').length);
  var i = 1;
  var pages = document.getElementById('sequential_pages').children;
  for(var j = 0; j < pages.length; j++) {
    pages[j].querySelector('.title-label').innerHTML = 'Page ' + i;
    pages[j].getElementsByTagName('textarea')[0].setAttribute('name', 'details-p' + i);
    pages[j].querySelectorAll('input[type=checkbox]')[0].setAttribute('id', 'score_engine_enable_' + i);
    pages[j].querySelectorAll('input[type=text]')[0].setAttribute('id', 'score_engine_value_' + i);
    pages[j].getElementsByClassName('button')[0].setAttribute('for', 'fileUpload1-p' + i);
    pages[j].querySelectorAll('input[type=file]')[0].setAttribute('id', 'fileUpload1-p' + i);
    pages[j].querySelectorAll('input[type=file]')[0].setAttribute('name', 'fileUpload1-p' + i);
    pages[j].querySelectorAll('input[type=file]')[0].setAttribute('onchange', "displayUploadedFiles(this, 'files-p" + i + "');");
    i++;
  }
}

$('#score_engine_enable_1').change(function() {
  var enabled = $('#score_engine_enable_1').is(':checked');
  if(enabled) {
    $('#score_engine_value_1').prop('disabled',false);
  } else {
    $('#score_engine_value_1').prop('disabled',true);
  }
});

function readURL(input) {
  if (input.files && input.files[0]) {
    var reader = new FileReader();

    reader.onload = function(e) {
      $('#image-preview').attr('src', e.target.result);
    }

    reader.readAsDataURL(input.files[0]); // convert to base64 string
  }
}

$("#lab-photo").change(function() {
  readURL(this);
});

function displayUploadedFiles(uploader, output_div) {
  txt = '';
  if ('files' in uploader) {
    if (uploader.files.length == 0) {
      txt = "Select one or more files.";
    } else {
      for (var i = 0; i < uploader.files.length; i++) {
        txt += "<br><strong>";
        var file = uploader.files[i];
        if ('name' in file) {
          txt += file.name;
        }
        if ('size' in file) {
          txt += '(' + file.size + " bytes) <br>";
        } else {
          txt += "<br>";
        }
        txt += "</strong>";
      }
    }
  }
  else {
    if (uploader.value == "") {
      txt += "Select one or more files.";
    } else {
      txt += "The files property is not supported by your browser!";
      txt  += "<br>The path of the selected file: " + uploader.value; // If the browser does not support the files property, it will return the path of the selected file instead.
    }
  }
  document.getElementById(output_div).innerHTML = txt;
}
