$(document).ready(function(){
  $('#search-query').on('input', function(){
    const query = $(this).val();
    const category = $('#search-category').val();
    const resultsContainer = $('#search-results');
    resultsContainer.empty();

    if(query.length > 2){
      $.ajax({
        url: 'search-friend',
        data: {
          'q': query,
          'category': category
        },
        dataType: 'json',
        success: function(data){
          data.results.forEach(function(user){
            const li = $('<li></li>').text(user.display_name).attr('data-user-id', user.id);
            resultsContainer.append(li);

            li.on('click', function(){
              $('#selected-user-id').val($(this).data('userId'));
              $('#search-query').val($(this).text());
              resultsContainer.empty();
            });
          });
        }
      });
    }
  });
});