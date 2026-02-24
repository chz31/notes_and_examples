`dataset_name_or_id: 1` in Windows did not work. `\\` also did not work. Try this `input.yaml` in Windows:

```
modality: CT
dataset_name_or_id: "Dataset001_OrbitCT"
datalist: "C:/m/msd_monai_nnunet_tr_folds.json"
dataroot: "C:/m/monai_nn_tr"
nnunet_preprocessed: "C:/m/p/nnUNet_preprocessed"
nnunet_raw: "C:/m/nnUNet_raw_data_base"
nnunet_results: "C:/m/o/nnUNet_trained_models"
```
