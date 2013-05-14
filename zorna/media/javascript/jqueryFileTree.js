// jQuery File Tree Plugin
//
// Version 1.01
//
// Cory S.N. LaViska
// A Beautiful Site (http://abeautifulsite.net/)
// 24 March 2008
//
// Visit http://abeautifulsite.net/notebook.php?article=58 for more information
//
// Usage: $('.fileTreeDemo').fileTree( options, callback )
//
// Options:  root           - root folder to display; default = /
//           script         - location of the serverside AJAX file to use; default = jqueryFileTree.php
//           folderEvent    - event to trigger expand/collapse; default = click
//           expandSpeed    - default = 500 (ms); use -1 for no animation
//           collapseSpeed  - default = 500 (ms); use -1 for no animation
//           expandEasing   - easing function to use on expand (optional)
//           collapseEasing - easing function to use on collapse (optional)
//           multiFolder    - whether or not to limit the browser to one subfolder at a time
//           loadMessage    - Message to display while initial tree loads (can be HTML)
//
// History:
//
// 1.01 - updated to work with foreign characters in directory/file names (12 April 2008)
// 1.00 - released (24 March 2008)
//
// TERMS OF USE
// 
// This plugin is dual-licensed under the GNU General Public License and the MIT License and
// is copyright 2008 A Beautiful Site, LLC. 
//
if(jQuery) (function($){
	
	$.extend($.fn, {
		fileTree: function(o, h) {
			// Defaults
			if( !o ) var o = {};
			if( o.root == undefined ) o.root = '/';
			if( o.script == undefined ) o.script = 'jqueryFileTree.php';
			if( o.folderEvent == undefined ) o.folderEvent = 'click';
			if( o.expandSpeed == undefined ) o.expandSpeed= 500;
			if( o.collapseSpeed == undefined ) o.collapseSpeed= 500;
			if( o.expandEasing == undefined ) o.expandEasing = null;
			if( o.collapseEasing == undefined ) o.collapseEasing = null;
			if( o.multiFolder == undefined ) o.multiFolder = true;
			if( o.loadMessage == undefined ) o.loadMessage = 'Loading...';
			if( o.folderHandler == undefined ) o.folderHandler = null;
			
			$(this).each( function() {
				
				function showTree(c, t) {
					$(c).addClass('wait');
					$(".jqueryFileTree.start").remove();
					$.get(o.script, { dir: t }, function(data) {
						$(c).find('.start').html('');
						$(c).removeClass('wait').append(data);
						if( o.root == t ) $(c).find('UL:hidden').show(); else $(c).find('UL:hidden').slideDown({ duration: o.expandSpeed, easing: o.expandEasing });
						bindTree(c);
						//if( o.folderHandler) {o.folderHandler(t);}
					});
				}
				
				function bindTree(t) {
					$(t).find('LI A').livequery(o.folderEvent, function() {
						if( $(this).parent().hasClass('directory') ) {
							if( $(this).parent().hasClass('collapsed') ) {
								// Expand
								if( !o.multiFolder ) {
									$(this).parent().parent().find('UL').slideUp({ duration: o.collapseSpeed, easing: o.collapseEasing });
									$(this).parent().parent().find('LI.directory').removeClass('expanded').addClass('collapsed');
								}
								$(this).parent().find('UL').remove(); // cleanup
								showTree( $(this).parent(), escape($(this).attr('rel').match( /.*\// )) );
								$(this).parent().removeClass('collapsed').addClass('expanded');
								if( o.folderHandler) {o.folderHandler($(this).attr('rel'));}
							} else {
								// Collapse
								$(this).parent().find('UL').slideUp({ duration: o.collapseSpeed, easing: o.collapseEasing });
								$(this).parent().removeClass('expanded').addClass('collapsed');
							}
						} else {
							h($(this).attr('rel'));
						}
						return false;
					});
					// Prevent A from triggering the # on non-click events
					if( o.folderEvent.toLowerCase != 'click' ) $(t).find('LI A').livequery('click', function() { return false; });
				}
				// Loading message
				$(this).html('<ul class="jqueryFileTree start"><li class="wait">' + o.loadMessage + '<li></ul>');
				// Get the initial file list
				showTree( $(this), escape(o.root) );
			});
		}
	});
	
})(jQuery);

/**
 * Cookie plugin
 *
 * Copyright (c) 2006 Klaus Hartl (stilbuero.de)
 * Dual licensed under the MIT and GPL licenses:
 * http://www.opensource.org/licenses/mit-license.php
 * http://www.gnu.org/licenses/gpl.html
 *
 */

jQuery.cookie = function(name, value, options) {
    if (typeof value != 'undefined') { // name and value given, set cookie
        options = options || {};
        if (value === null) {
            value = '';
            options.expires = -1;
        }
        var expires = '';
        if (options.expires && (typeof options.expires == 'number' || options.expires.toUTCString)) {
            var date;
            if (typeof options.expires == 'number') {
                date = new Date();
                date.setTime(date.getTime() + (options.expires * 24 * 60 * 60 * 1000));
            } else {
                date = options.expires;
            }
            expires = '; expires=' + date.toUTCString(); // use expires attribute, max-age is not supported by IE
        }
        // CAUTION: Needed to parenthesize options.path and options.domain
        // in the following expressions, otherwise they evaluate to undefined
        // in the packed version for some reason...
        var path = options.path ? '; path=' + (options.path) : '';
        var domain = options.domain ? '; domain=' + (options.domain) : '';
        var secure = options.secure ? '; secure' : '';
        document.cookie = [name, '=', encodeURIComponent(value), expires, path, domain, secure].join('');
    } else { // only name given, get cookie
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
};
