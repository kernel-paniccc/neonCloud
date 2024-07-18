        $(function() {
          $('a#test').on('click', function(e) {
            e.preventDefault()
            $.getJSON('/send_reset_code',
                function(data) {
              //do nothing
            });
            return false;
          });
        });