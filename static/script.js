function form_table(){
    const nb_col = document.getElementById('nb_colonnes').value;
    document.getElementById('form_table').innerHTML = "";
    for (let i = 1; i <= nb_col; i++) {
        document.getElementById('form_table').innerHTML +=
            `<br><label for="nom-colonne-${i}">Nom colonne ${i}</label><br>
            <input type="text" id="nom-colonne-${i}" name="nom-colonne-${i}" class="form-control" required><br>
            <label for="type-colonne-${i}">Type colonne ${i}</label><br>
            <select id="type-colonne-${i}" name="type-colonne-${i}" required class="form-select">
                <option selected>Selectionner un type</option>
                <option value="INT AUTO_INCREMENT">compteur</option>
                <option value="INT">int</option>
                <option value="VARCHAR(255)">varchar</option>
                <option value="DATE">date</option>
                <option value="DATETIME">datetime</option>
                <option value="TIME">time</option>
                <option value="DECIMAL(19,4)">decimal</option>
                <option value="BOOLEAN">boolean</option>
            </select><br>
            <label for="primary-key-${i}">Clé primaire ?</label><br>
            <input type="checkbox" name="primary-key-${i}" id="primary-key-${i}" class="form-check"><br>`;
    }
    document.getElementById('form_table').innerHTML += `<button type="submit" class="btn-success btn">Créer</button>`;
}