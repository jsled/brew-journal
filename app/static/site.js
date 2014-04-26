
function toggle_node_visibility(node)
{
    node.style['display'] = (node.style['display'] == 'none' ? '' : 'none');
}

function toggle_visibility(base_name)
{
    toggle_node_visibility(document.getElementById(base_name));
    toggle_node_visibility(document.getElementById(base_name + '-alt'));
}


var bj = (function($) {
    // recipe/view.html:
    $(function () {
        $('select[name=usage_type]').change(function(evt) {
            var select = $(this);
            var selected = $('option:selected', select);
            var containing_td = select.closest('td');
            var boil_minutes_span = $('.hop_boil_minutes', containing_td);
            var minutes_visible = (selected.val() == 'boil');
            if (minutes_visible) {
                boil_minutes_span.show();
            } else {
                var boil_minutes = $('input[name=boil_time]', containing_td);
                boil_minutes.val(0);
                boil_minutes_span.hide();
            }
        });
    });

    $(function _bj_init() {
        $(document).on('click', '.bj-js-toggle-next', function _bj_toggle_next() {
            $(this).closest('DIV').next('.bj-js-toggle').children().slideToggle();
        });

        $(document).on('click', '.bj-js-toggle-parent', function _bj_toggle_parent() {
            $(this).closest('DIV.bj-js-toggle').children().slideToggle();
        });

        $(document).on('click', '.bj-js-edit-cancel', function _bj_edit_cancel() {
            // don't prevent default action to allow form reset.
            $(this).closest('.bj-js-toggle').children().slideToggle();
        });

    });


    $(function _bj_recipe_handlers() {
        $(document).on('click', '.bj-js-recipe-item-edit', function _bj_recipe_item_edit(evt) {
            evt.preventDefault();
            var $row = $(this).closest('.bj-item-display.row');
            $row.toggle();
            $row.next('.bj-item-editor.row').toggle();
            // $(this).closest('.row + .row.editor').toggle();
        });

        $(document).on('click', '.bj-js-recipe-item-delete', function _bj_recipe_item_delete(evt) {
            evt.preventDefault();
            var $row = $(this).closest('.bj-item-display.row');
            var id = $row.data('bj-item-id');
            var $form = $(this).closest('.bj-item-display.row + .bj-item-editor.row').find('FORM');
            $form.find('INPUT[name=delete_id]').val(id);
            $form.submit();
        });

        $(document).on('click', '.bj-js-recipe-item-add', function _bj_recipe_item_add(evt) {
            evt.preventDefault();
            var $row = $(this).closest('.bj-item-add.row');
            $row.toggle();
            $row.next('.bj-item-editor.row').toggle();
        });

        $(document).on('click', 'INPUT[type=reset].bj-js-recipe-item-edit-cancel', function _bj_recipe_item_edit_cancel(evt) {
            var $editor = $(this).closest('.bj-item-editor.row');
            var $display = $editor.prev('.row');
            $editor.toggle()
            $display.toggle();
            // let default action (form reset) continue
        });

        $(document).on('click', '.bj-js-recipe-details-edit', function _bj_recipe_details_edit(evt) {
            evt.preventDefault();
            $(this).closest('DIV').next('.bj-js-toggle').children().slideToggle();
            $('#overview-form :input:first').focus();
        });

    });

    // user/brew/index.html
    $(function _bj_user_brew_init() {
        $(document).on('click', '.bj-js-brew-step-add', function _bj_brew_step_add(evt) {
            evt.preventDefault();
            $(this).closest('.bj-js-toggle').children().slideToggle();
        });

        $(document).on('click', '.bj-js-brew-step-delete', function _bj_brew_step_delete(evt) {
            var $row = $(this).closest('[data-step-url]');
            // console.log('delete',$$x, $$x.data('brew-id'), $$x.data('step-id'),$$x.data('step-url'));
            jQuery.ajax($row.data('step-url'), {type:'DELETE', dataType:'json'})
                .done(function _deleteSuccess(data) {
                    window.location = data.brew_url;
                })
                .fail(function _deleteFail(jqXhr, status, errorThrown) {
                    console.log('error',status,errorThrown);
                });
        });

    });

    return {
        
    };

})(jQuery);
