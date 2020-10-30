function addLabPage() {
  var pageCount = $('.total-page-count').length;
  var page = `<div class="medium-6 cell"><label>Page ${pageCount + 1} Title<input type="text" placeholder="Pre-Lab Setup"
  name="title-p${pageCount+1}"></label></div><div class="medium-6 cell"><label>Assignment Details<textarea style="height:100px;"
    placeholder="Step 1: boot up your VM..." name="details-p${pageCount+1}"></textarea></label></div><div class="medium-6 cell">
    <label>Scoring Engine Hash value&nbsp;<input type="checkbox" id="score_engine_enable_${pageCount+1}"><input type="text"
    placeholder="0xc0ffee" disabled id="score_engine_value_${pageCount+1}"/></label></div><div class="medium-6 cell">
    <label for="fileUpload1-p${pageCount + 1}" class="button">Upload External Media</label><input type="file"
    id="fileUpload1-p${pageCount + 1}"class="show-for-sr" name="fileUpload1-p${pageCount + 1}"></div><input type="hidden"
    class="total-page-count"/>`;
  $('#sequential_pages').html($('#sequential_pages').html() + page);

  $('#score_engine_enable_' + (pageCount + 1)).change(function() {
    var enabled = $('#score_engine_enable_' + (pageCount + 1)).is(':checked');
    if(enabled) {
      $('#score_engine_value_' + (pageCount + 1)).prop('disabled',false);
    } else {
      $('#score_engine_value_' + (pageCount + 1)).prop('disabled',true);
    }
  });
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
