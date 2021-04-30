function addLabPage() {
  var pageCount = $('.total-page-count').length + 1;
  $('#total-page-count').val(pageCount);
  var page = `<section id="page_${pageCount}" data-magellan-target="page_${pageCount}"><div><div class="cell"><label class="title-label">Page ${pageCount} Title \n<input type="text" placeholder="Pre-Lab Setup" name="title-p${pageCount}">\n</label></div><div class="cell"><label>Assignment Details <textarea style="height:100px;" placeholder="Step 1: boot up your VM..." name="details-p${pageCount}"></textarea></label></div><label>Scoring Engine Hash value&nbsp;<input type="checkbox" id="score_engine_enable_${pageCount}"></label><div id="scoring_engine_${pageCount}" style="display: none" class="cell"><div class="input-group"><span class="input-group-label">Answer Prompt</span><input class="input-group-field" placeholder="Input the Hash" type="text" id="score_engine_prompt_${pageCount}" name="score_engine_prompt_${pageCount}"></div><div class="input-group"><span class="input-group-label">Answer and Difficulty</span><input class="input-group-field" type="text" placeholder="0xc0ffee" id="score_engine_value_${pageCount}" name="score_engine_value_${pageCount}"><div class="input-group-field"><select class="input-group-field" name="answer_difficulty_${pageCount}"><option value="1">Trivial</option><option value="2">Easy</option><option value="3">Medium</option><option value="4">Hard</option></select></div></div></div><div class="cell"><div id="files-p${pageCount}"></div><label for="fileUpload1-p${pageCount}" class="button">Upload External Media</label><input type="file" multiple id="fileUpload1-p${pageCount}" class="show-for-sr" name="fileUpload1-p${pageCount}" onchange="displayUploadedFiles(this, 'files-p${pageCount}');">\n<input class="button" style="background-color:red;" onclick ="removeLabPage(event);" value="Remove Page"/></div><input type="hidden" class="total-page-count"></div><hr style="border-bottom: 1px dashed #c3c3c3;"></section>`;
  document.getElementById('sequential_pages').insertAdjacentHTML("beforeend", page);

  $('#score_engine_enable_' + pageCount).change(function() {
    var enabled = $('#score_engine_enable_' + pageCount).is(':checked');
    if(enabled) {
      $('#scoring_engine_' + pageCount).css('display', '');
    } else {
      $('#scoring_engine_' + pageCount).css('display', 'none');
    }
  });

  var new_contents = `<li style="background-color: lightseagreen; color: white;font-weight: 600;">Lab Editor</li><li><a href="#lab_details">Lab Details</a></li>`;
  for(var i = 0; i < pageCount; i++){
    new_contents += `<li><a href="#page_${i+1}">Page ${i+1}<i style="color: red; float: right;" class="fi-x" title="Delete Page"></i></a></li>`;
  }
  new_contents += `<li><a href="#publish">Publish Lab</a></li>`;
  $('#contents').html(new_contents);
}

function removeLabPage(event) {
  var page_num = event.currentTarget.parentNode.children[0].id.slice(-1);
  document.getElementById('page_' + page_num).remove();
  $('#total-page-count').val($('.total_page_count').length);
  var i = 1;
  var pages = document.getElementById('sequential_pages').children;
  for(var j = 0; j < pages.length; j++) {
    if(pages[j].tagName != 'HR') {
      var elements = pages[j].querySelector('.title-label').innerHTML.split('\n');
      if(elements[0] == ''){
        elements = elements.slice(1);
      }
      elements[0] = 'Page ' + i + ' Title';
      pages[j].querySelector('.title-label').innerHTML = elements.join('\n');
      pages[j].querySelectorAll('input[type=text]')[0].setAttribute('name', 'title-p' + i);
      pages[j].getElementsByTagName('textarea')[0].setAttribute('name', 'details-p' + i);
      pages[j].querySelectorAll('input[type=checkbox]')[0].setAttribute('id', 'score_engine_enable_' + i);
      pages[j].querySelectorAll('input[type=text]')[1].setAttribute('id', 'score_engine_prompt_' + i);
      pages[j].querySelectorAll('input[type=text]')[1].setAttribute('name', 'score_engine_prompt_' + i);
      pages[j].querySelectorAll('input[type=text]')[2].setAttribute('id', 'score_engine_value_' + i);
      pages[j].querySelectorAll('input[type=text]')[2].setAttribute('name', 'score_engine_value_' + i);
      pages[j].querySelectorAll('select')[0].setAttribute('name', 'answer_difficulty_' + i);
      pages[j].getElementsByClassName('button')[0].setAttribute('for', 'fileUpload1-p' + i);
      pages[j].querySelectorAll('input[type=file]')[0].setAttribute('id', 'fileUpload1-p' + i);
      pages[j].querySelectorAll('input[type=file]')[0].setAttribute('name', 'fileUpload1-p' + i);
      pages[j].querySelectorAll('input[type=file]')[0].setAttribute('onchange', "displayUploadedFiles(this, 'files-p" + i + "');");
      i++;
    }
  }
  var new_contents = `<li style="background-color: lightseagreen; color: white;font-weight: 600;">Lab Editor</li><li><a href="#lab_details">Lab Details</a></li>`;
  for(var i = 0; i < pages.length-1; i++){
    new_contents += `<li><a href="#page_${i+1}">Page ${i+1}<i style="color: red; float: right;" class="fi-x" title="Delete Page"></i></a></li>`;
  }
  new_contents += `<li><a href="#publish">Publish Lab</a></li>`;
  $('#contents').html(new_contents);
}

$('#score_engine_enable_1').change(function() {
  var enabled = $('#score_engine_enable_1').is(':checked');
  if(enabled) {
    $('#scoring_engine_1').css('display', '');
  } else {
    $('#scoring_engine_1').css('display', 'none');
  }
});

function readURL(input) {
  if (input.files && input.files[0]) {
    var reader = new FileReader();
    reader.onload = function(e) {
      document.getElementById('image-preview').style.backgroundImage = 'url("' + e.target.result + '")';
      document.getElementById('upload-check').checked = true;
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
