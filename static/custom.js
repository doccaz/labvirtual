function startVM(vm_name) {

  $.get("/labvirtual/startvm?name=" + vm_name);
  //$.get("/labvirtual/startvm?name=" + vm_name, function(data, status){
  //    alert("Data: " + data + "\nStatus: " + status);
  //  });
  var popup = document.getElementById("myPopup");
  popup.classList.toggle("show");
}

