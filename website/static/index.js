<<<<<<< HEAD
function deleteNote(noteId) {
 

    fetch("/delete-note", {
   
  
      method: "POST",
   
  
      body: JSON.stringify({ noteId: noteId }),
   
  
    }).then((_res) => {
   
  
      window.location.href = "/";
   
  
    });
   
  
=======
function deleteNote(noteId) {
 

    fetch("/delete-note", {
   
  
      method: "POST",
   
  
      body: JSON.stringify({ noteId: noteId }),
   
  
    }).then((_res) => {
   
  
      window.location.href = "/";
   
  
    });
   
  
>>>>>>> 11087191ba6c9c67c5ba75a139af05d657e2bf97
  }