# smpleconverter

Di principio, la conversione dei modelli è progettata per prendere in input le mesh .obj o .ply, dalle quali estrae i vertici e le facce del modello, per andare ad ottimizzare un modello SMPL a partire da quei parametri provenienti da SMPL-X. Ho esteso il dataloader di questo modulo per poter caricare direttamente dei modelli SMPL-X, dai quali andare poi ad estrarre facce e vertici in modo tale da lasciare invariato il fitting successivo del modello SMPL. Gli step per eseguirlo sono:

1.  Scaricare i modelli SMPL-X (MALE, FEMALE, NEUTRAL) e metterli in transfer_data/meshes/smplx: https://smpl-x.is.tue.mpg.de/
2.  Scaricare i modelli SMPL (MALE, FEMALE, NEUTRAL), rinominarli in (SMPL_MALE.pkl, SMPL_FEMALE.pkl, SMPL_NEUTRAL.pkl) e metterli in transfer_data/meshes/smpl: https://smpl.is.tue.mpg.de/
3.  Scaricare la KID TEMPLATE e rinominarla in SMPLX_KID_TEMPLATE.npy, e metterla in transfer_data/meshes/smplx: https://agora.is.tue.mpg.de/

Il formato dovrà essere il seguente
```
transfer_data
├── meshes
│   ├── smpl
│   ├── smplx
├── smpl2smplh_def_transfer.pkl
├── smpl2smplx_deftrafo_setup.pkl
├── smplh2smpl_def_transfer.pkl
├── smplh2smplx_deftrafo_setup.pkl
├── smplx2smpl_deftrafo_setup.pkl
├── smplx2smplh_deftrafo_setup.pkl
├── smplx_mask_ids.npy
```
dove i .pkl di conversione aggiuntivi sono da scaricare sempre dal repository di SMPL-X (http://smpl-x.is.tue.mpg.de/)

4. per buildare:
     ```
     cd smpleconverter/docker
     ./build.sh
     ```

 5. per runnare bisogna specificare la directory contenente i dati
      ```
      ./run -d /path/to/data
      ```
6. per lanciare la conversione:
    ```
    cd src
    python -m transfer_model --exp-cfg config_files/smplx2smpl.yaml
    ```

    prima di convertire, è necessario impostare i parametri di conversione in ```config_files/smplx2smpl.yaml```, ovviamente bisogna cambiare i path di data_folder e output_folderr:
   ```
   datasets:
    name: "smplx" // PER ORA USIAMO IL DATALOADER CUSTOM CHE HO SCRITTO PER USARE DIRETTAMENTE I MODELLI SMPL-X, E NON MESH .obj
    mesh_folder:
        data_folder: '/home/daniel/Data/PROCESSED_DATA/s05/s05_a08/smplx/' // QUESTA DEVE ESSERE LA DIRECTORY CONTENENTE I FILE SMPL-X DA CONVERTIRE
        
    deformation_transfer_path: 'transfer_data/smplx2smpl_deftrafo_setup.pkl'
    mask_ids_fname: ''
    summary_steps: 100
    
    edge_fitting:
        per_part: False
    
    optim:
        type: 'lbfgs'
        maxiters: 200
        gtol: 1e-06

   output_folder: '/home/daniel/Data/PROCESSED_DATA/s05/s05_a08/smpl/' // DOVE VERRANNO SALVATI I MODELLI SMPL .pkl (L'EXPORT DEGLI .obj è DISATTIVATA)
    
    body_model:
        model_type: "smpl"
        gender: "male"
        ext: 'pkl'
        folder: "/home/daniel/src/transfer_data/meshes" // QUESTA DIRECTORY PUNTA AI MODELLI DI BASE DI SMPL E SMPL-X, L'OUTPUT DEL COMANDO "ls" QUI DENTRO DEVE RESTITUIRE "smpl smplx"
        use_compressed: False
        use_face_contour: False
        smpl:
            betas:
                num: 10
    
    batch_size: 16 // BATCH SIZE A PIACIMENTO, NON IMPATTA TROPPO SULLA VRAM
   ```
7. Se si spacca in ```transfer_model/data/datasets``` la ```read_config``` o ```read_smplx_model```, è perché manca il file di dump del fitting del modello SMPL-X fatto tramite la repository smplreconstruction. Eventualmente possiamo trovare un'altro modo per recuperare quelle info (gender, age, num_pca_comps)
    
