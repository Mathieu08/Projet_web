function onTitleChange() {
	var champIdentifiant = document.getElementById('ident')
	var titre = document.getElementById('titre').value;

	if (titre === "") {
		champIdentifiant = "";
	}else {
		var xhr = new XMLHttpRequest();
		xhr.onreadystatechange = function() {
			if (xhr.readyState === XMLHttpRequest.DONE) {
				if (xhr.status === 200) {
					result = JSON.parse(xhr.responseText);
					champIdentifiant.value = result.identifiant;
				}else {
					console.log('Erreur avec le serveur');
				}
			}
		};

		xhr.open("GET", "/identifiant/"+titre, true);
		xhr.send();
	}
}

function onIdentChange() {
	var ident = document.getElementById('ident').value;

	var xhr = new XMLHttpRequest();
		xhr.onreadystatechange = function() {
			if (xhr.readyState === XMLHttpRequest.DONE) {
				if (xhr.status === 200) {
					document.getElementById('err').innerHTML = xhr.responseText;
				}else {
					console.log('Erreur avec le serveur');
				}
			}
		};

		xhr.open("GET", "/verif-identifiant/"+ident, true);
		xhr.send();
}