var currentSideBar = 'div#title_side_bar';
function changeSideBar(enabled_bar) {
    $(currentSideBar).hide();
    currentSideBar = enabled_bar;
    $(currentSideBar).fadeIn('slow');

}

$(function () {
    $('div#editor_side_bar').hide();
    $('div#tags_side_bar').hide();

    $('#id_title').focus(function(){changeSideBar('div#title_side_bar')});
    $('#editor').focus(function(){changeSideBar('div#editor_side_bar')});
    $('#id_tags').focus(function(){changeSideBar('div#tags_side_bar')});
});

$(function() {
    var $input = $('#id_title');
    var $box = $('#ask-related-questions');
    var template = $('#question-summary-template').html();

    var results_cache = {};

    function reload_suggestions_box(e) {
        var relatedQuestionsDiv = $('#ask-related-questions');
        var q = $input.val().replace(/^\s+|\s+$/g,"");

        if(q.length == 0) {
            close_suggestions_box();
            relatedQuestionsDiv.html('');
            return false;
        } else if(relatedQuestionsDiv[0].style.height == 0 || relatedQuestionsDiv[0].style.height == '0px') {
            relatedQuestionsDiv.animate({'height':'150'}, 350);
        }

        if (results_cache[q] && results_cache[q] != '') {
            relatedQuestionsDiv.html(results_cache[q]);
            return false;
        }

        $.post(related_questions_url, {title: q}, function(data) {
            if (data) {
                var c = $input.val().replace(/^\s+|\s+$/g,"");

                if (c != q) {
                    return;
                }

                if(data.length == 0) {
                    relatedQuestionsDiv.html('<br /><br /><div align="center">No questions like this have been found.</div>');
                    return;
                }

                var html = '';
                for (var i = 0; i < data.length; i++) {
                    var item = template.replace(new RegExp('%URL%', 'g'), data[i].url)
                                       .replace(new RegExp('%SCORE%', 'g'), data[i].score)
                                       .replace(new RegExp('%TITLE%', 'g'), data[i].title)
                                       .replace(new RegExp('%SUMMARY%', 'g'), data[i].summary);

                    html += item;

                }

                results_cache[q] = html;

                relatedQuestionsDiv.html(html);
            }
        }, 'json');

        return false;
    }

    function close_suggestions_box() {
        $('#ask-related-questions').animate({'height':'0'},350, function() {
            $('#ask-related-questions').html('');
        });
    }

    $input.keyup(reload_suggestions_box);
    $input.focus(reload_suggestions_box);
    $input.blur(close_suggestions_box);

    // for chrome
    $input.keydown(focus_on_question);
    function focus_on_question(e) {
        var is_chrome = navigator.userAgent.toLowerCase().indexOf('chrome') > -1;

        if(e.keyCode == 9 && is_chrome) {
            $('#editor')[0].focus();
        }
    }
});