var windowFocus = true;
var originalTitle;
var blinkOrder = 0;
var bNewMessage = false;


/*!!
 * Title Alert 0.7
 * 
 * Copyright (c) 2009 ESN | http://esn.me
 * Jonatan Heyman | http://heyman.info
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 */
 
/* 
 * @name jQuery.titleAlert
 * @projectDescription Show alert message in the browser title bar
 * @author Jonatan Heyman | http://heyman.info
 * @version 0.7.0
 * @license MIT License
 * 
 * @id jQuery.titleAlert
 * @param {String} text The text that should be flashed in the browser title
 * @param {Object} settings Optional set of settings.
 *	 @option {Number} interval The flashing interval in milliseconds (default: 500).
 *	 @option {Number} originalTitleInterval Time in milliseconds that the original title is diplayed for. If null the time is the same as interval (default: null).
 *	 @option {Number} duration The total lenght of the flashing before it is automatically stopped. Zero means infinite (default: 0).
 *	 @option {Boolean} stopOnFocus If true, the flashing will stop when the window gets focus (default: true).
 *   @option {Boolean} stopOnMouseMove If true, the flashing will stop when the browser window recieves a mousemove event. (default:false).
 *	 @option {Boolean} requireBlur Experimental. If true, the call will be ignored unless the window is out of focus (default: false).
 *                                 Known issues: Firefox doesn't recognize tab switching as blur, and there are some minor IE problems as well.
 *
 * @example $.titleAlert("Hello World!", {requireBlur:true, stopOnFocus:true, duration:10000, interval:500});
 * @desc Flash title bar with text "Hello World!", if the window doesn't have focus, for 10 seconds or until window gets focused, with an interval of 500ms
 */
;(function($){	
	$.titleAlert = function(text, settings) {
		// check if it currently flashing something, if so reset it
		if ($.titleAlert._running)
			$.titleAlert.stop();

		// override default settings with specified settings
		$.titleAlert._settings = settings = $.extend( {}, $.titleAlert.defaults, settings);

		// if it's required that the window doesn't have focus, and it has, just return
		if (settings.requireBlur && $.titleAlert.hasFocus)
			return;

		// originalTitleInterval defaults to interval if not set
		settings.originalTitleInterval = settings.originalTitleInterval || settings.interval;

		$.titleAlert._running = true;
		$.titleAlert._initialText = document.title;
		document.title = text;
		var showingAlertTitle = true;
		var switchTitle = function() {
			// WTF! Sometimes Internet Explorer 6 calls the interval function an extra time!
			if (!$.titleAlert._running)
				return;

		    showingAlertTitle = !showingAlertTitle;
		    document.title = (showingAlertTitle ? text : $.titleAlert._initialText);
		    $.titleAlert._intervalToken = setTimeout(switchTitle, (showingAlertTitle ? settings.interval : settings.originalTitleInterval));
		}
		$.titleAlert._intervalToken = setTimeout(switchTitle, settings.interval);

		if (settings.stopOnMouseMove) {
			$(document).mousemove(function(event) {
				$(this).unbind(event);
				$.titleAlert.stop();
			});
		}

		// check if a duration is specified
		if (settings.duration > 0) {
			$.titleAlert._timeoutToken = setTimeout(function() {
				$.titleAlert.stop();
			}, settings.duration);
		}
	};

	// default settings
	$.titleAlert.defaults = {
		interval: 500,
		originalTitleInterval: null,
		duration:0,
		stopOnFocus: true,
		requireBlur: false,
		stopOnMouseMove: false
	};

	// stop current title flash
	$.titleAlert.stop = function() {
		if (!$.titleAlert._running)
			return;

		clearTimeout($.titleAlert._intervalToken);
		clearTimeout($.titleAlert._timeoutToken);
		document.title = $.titleAlert._initialText;

		$.titleAlert._timeoutToken = null;
		$.titleAlert._intervalToken = null;
		$.titleAlert._initialText = null;
		$.titleAlert._running = false;
		$.titleAlert._settings = null;
	}

	$.titleAlert.hasFocus = true;
	$.titleAlert._running = false;
	$.titleAlert._intervalToken = null;
	$.titleAlert._timeoutToken = null;
	$.titleAlert._initialText = null;
	$.titleAlert._settings = null;


	$.titleAlert._focus = function () {
		$.titleAlert.hasFocus = true;

		if ($.titleAlert._running && $.titleAlert._settings.stopOnFocus) {
			var initialText = $.titleAlert._initialText;
			$.titleAlert.stop();

			// ugly hack because of a bug in Chrome which causes a change of document.title immediately after tab switch
			// to have no effect on the browser title
			setTimeout(function() {
				if ($.titleAlert._running)
					return;
				document.title = ".";
				document.title = initialText;
			}, 1000);
		}
	};
	$.titleAlert._blur = function () {
		$.titleAlert.hasFocus = false;
	};

	// bind focus and blur event handlers
	$(window).bind("focus", $.titleAlert._focus);
	$(window).bind("blur", $.titleAlert._blur);
})(jQuery);




function loadTabs(tab, community_id) {
  param = "tab="+tab;
  jQuery.ajax({
    url: 'form/'+tab+'/?community_id='+community_id,
    cache: false,
    dataType: "json",
    success: function(data) {
      	$("#share_post_text").html(data.html);
      	members_data = data.sendto;
		$(".com_recipients").multiselect({completions: members_data, enable_new_options: false});
		$('#id_attachments').MultiFile();		
    }});
}

function display_profile(id) {
	$.facebox(function() {
		$.facebox.loading(); 
	  	jQuery.get('/communities/member/profile/'+id+'/', function(data) {
	    	jQuery.facebox(data)
	  })
	})
}

function updateMessage(value, settings) {
  var msgid = $(this).attr('msgid');
  param = "msgid="+msgid+"&value="+value;
  jQuery.ajax({
    url: 'message/update_message/',
    cache: false,
    data: param,
    dataType: "json",
    success: function(data) {
      if ( data.error ==  false) {
        var idElem = $("p[id=msg_entry_text-"+data.msgid+"]");
        $(idElem).html(data.message);
      }
    }});
  return value;
}
      
function bind_reply_click()
{
  $("a[id^=a-]").click(function(event) {
    var elId = event.currentTarget.id;
    elId = 'msg_entry_reply-'+elId;
    $('#'+elId).toggle(400);
    return false;
  });
  
  $("input[id^=msg_entry_send-]").click(function(event) {
    var msgid = $(this).attr('msgid');
    $("#msg_entry_reply-a-"+msgid).hide();
    $("#msg_entry_reply-wait-"+msgid).show();
    param = "reply_message="+$("textarea[id=reply_message-"+msgid+"]").val();
    param += "&msg_id="+ msgid;
    
    jQuery.ajax({
      url: "message/send_reply/",
      cache: false,
      data: param,
      dataType: "json",
      success: function(data) {
        if( data.msgid ) {
          idElem =  "#msg_entry-"+msgid;
          if($(idElem).length) {
            $(idElem).append(data.html);
          }
        }
        $("#msg_entry_reply-wait-"+msgid).hide();
      }
      });    
    return false;
  });


  $("p.msg_entry_edit").editable(updateMessage, {
    type      : 'textarea',
    event     : 'edit_reply',
    rows      : 3,
    cancel    : 'Cancel',
    submit    : 'Ok'
  });

  $("a[id^=a-edit-]").click(function(event) {
    var pid = "#msg_entry_text-"+$(this).attr('msgid');
    $(pid).trigger("edit_reply");
  });

  // delete reply message
  $("a[id^=a-rdelete-]").click(function(event) {
    var msgid = $(this).attr('msgid');
    param = "msgid="+msgid
    jQuery.ajax({
      url: "message/delete_reply/",
      cache: false,
      data: param,
      dataType: "json",
      success: function(data) {
        console.log(data);
        console.log("data.eroor="+data.error);
        if ( data.error ==  false) {
          $("div[id=reply_container-"+data.msgid+"]").remove();
          console.log("div[id=reply_container-"+data.msgid+"]");
        }
      }
      });    
    return false;

  });

  // delete message
  $("a[id^=a-delete-]").click(function(event) {
    var msgid = $(this).attr('msgid');
    param = "msgid="+msgid
    jQuery.ajax({
      url: "message/delete_message/",
      cache: false,
      data: param,
      dataType: "json",
      success: function(data) {
        console.log(data);
        console.log("data.eroor="+data.error);
        if ( data.error ==  false) {
          $("div[id=msg_container-"+data.msgid+"]").remove();
          console.log("div[id=reply_container-"+data.msgid+"]");
        }
      }
      });    
    return false;

  });
  
}

function msgHeartbeat(){
  
  var max_msg_id = 0;
  $("div[msgid]").each(function(i) {
      max_msg_id = Math.max(max_msg_id, $(this).attr('msgid'));
    }
  );
  param = "com_page="+com_page+"&community_id="+community_id+"&all_msg="+all_msg+"&msg_max_id="+max_msg_id+"&search_string="+search_string+"&member_id="+member_id+"&from_id="+from_id+"&message_id="+message_id;
  
  if ( windowFocus == false )
  {
    if (bNewMessage == false) {
      document.title = originalTitle;
    } else {
      document.title = "New Message";
    }
  }
  
  jQuery.ajax({
    url: "message/check_messages_ajax/",
    cache: false,
    data: param,
    dataType: "json",
    success: function(data) {
      if( data.html_messages.length) {
          //bNewMessage = true;
          $.titleAlert(new_message_text, {requireBlur:false,stopOnFocus:true, interval:700});
      }
      jQuery.each(data.html_messages, function(i,item){
        idElem =  "#msg_container-"+item.id;
        if($(idElem).length) {
          $(idElem).replaceWith(item.msg);
        }
        else {
          $("#msg_wrapper").prepend(item.msg);
          //$("#msg_entry_header-"+item.id).addClass('msg_entry_new');
        }
        
        $("div .msg_header").each(function(i) {
            if ( $(this).attr('msgid') > max_msg_id ) {
              $(this).addClass('msg_entry_new');
            }
            
          }
        );
      });
      //com_page = data.com_page;
      if( data.html_messages.length) {
      if( data.messages_more == false )
        $("#msg_more").hide();
      $("a[id^=a-]").unbind("click");  
      $("input[id^=msg_entry_send-]").unbind("click");
      bind_reply_click();
      }
    }});    
  setTimeout('msgHeartbeat();',60000);
  return false;
}

