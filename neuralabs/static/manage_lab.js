function addLabPage() {
  var pageCount = $('.total-page-count').length;
  var page = `<div class="medium-6 cell"><label>Page ${pageCount + 1} Title<input type="text" placeholder="Pre-Lab Setup" name="title-p${pageCount}">
    </label></div><div class="medium-6 cell"><label>Assignment Details<textarea style="height:100px;"
    placeholder="Step 1: boot up your VM..." name="details-p${pageCount}"></textarea></label></div><div class="medium-6 cell">
    <label for="fileUpload1-p${pageCount}" class="button">Upload External Media</label><input type="file" id="fileUpload1-p${pageCount}"
    class="show-for-sr" name="fileUpload1-p${pageCount}"></div><input type="hidden" class="total-page-count"/>`;
  $('#sequential_pages').html($('#sequential_pages').html() + page);
}
