
var qtip_options = { 
    content: {    
        text: ''
    },
    position: { adjust: { screen: true } },
    show: { solo: true },
    //hide: { when: 'inactive', delay: 3000 }, 
    style: { 
        width: 350,
        padding: 5,
        color: '#FFF',
        background: 'black',
        textAlign: 'left',
        border: {
        	width: 0,
        	radius: 3,
        	color: 'black'
     	},
     	tip: {corner: 'topLeft'}
    }
};

function update_folder(event) {
	var rel = $(this).attr('rel');
	param = "dir="+ rel;
	
	jQuery.ajax({
	  url: "browse/",
	  cache: false,
	  data: param,
	  dataType: "json",
	  success: function(data) {
	      idElem =  "#folder-content";
	      if($(idElem).length) {
			$(".file-properties").each( function(i) {
				$(this).qtip("destroy");
			});
	        $(idElem).html(data.content);
			$(".file-property").each( function(i) {
				qtip_options['content']['text'] = $(this).html();
				$("img#"+$(this).attr('id')).qtip(qtip_options);
			});
	        
	      }
	      idElem =  "#folder-right-path";
	      if($(idElem).length) {
	        $(idElem).html(data.path);
	      }
	      

			$(".check-box-file").click(function(){
				var nb = $(".check-box-file:checked");
				if (nb.length != 0){
					$("#bdelete").show();			
				} else {
					$("#bdelete").hide();			
				}
			});
	      
	  }
	  });    
	return false;
}

function updateDescription(value, settings) {
  param = "id="+this.id+"&value="+value;
  spanid = this.id;
  ret = value;
  jQuery.ajax({
    url: 'update/description/',
    cache: false,
    data: param,
    dataType: "json",
    success: function(data) {
      if(data.error != '') {
        $("span[id=error]").html(data.error).show(1000).fadeTo(5000, 1).hide(1000);
      }
    }});
  return value;
}

function rename(value, settings) {
  param = "id="+this.id+"&value="+value;
  spanid = this.id;
  ret = value;
  jQuery.ajax({
    url: 'renamefile/',
    cache: false,
    data: param,
    dataType: "json",
    success: function(data) {
      if(data.error == '') {
        $("span[id="+spanid+"]").attr('id', data.id);
        $("span[id="+spanid+"]").html(data.value);
      } else {
        $("span[id=error]").html(data.error).show(1000).fadeTo(5000, 1).hide(1000);
        $("span[id="+spanid+"]").html(data.value);
      }
    }});
  return value;
}

