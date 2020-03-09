
# atomagined 
#### A synthesized atomic-resolution HAADF STEM imaging dataset containing unique ICSD structure prototypes
###### *atomagined -  a portmanteau of atoms, imaged, imagined (the images are synthetic!)*

![image](https://drive.google.com/uc?export=view&id=13Jt07tCSwTN1WJaVU_9pKC3vbxhjXa9c)

## Introduction

The *atomagined* dataset is a collection of atomic-resolution images of unique [<b>ICSD</b>](http://www2.fiz-karlsruhe.de/icsd_home.html) structure prototypes, synthesized in the high angle annular dark field (HAADF) STEM modality. All images are calculated using [<b>PRISM</b>](http://prism-em.com/) imaging software, and post-processed to emulate noise and distortion conditions common to the HAADF STEM imaging mode. 

The dataset is structured as both a testbed for the development of image retrieval tools in atomic-resolution materials microscopy, containing a designated [<b>retrieval</b>](retrieval) dataset with [<b>targets</b>](targets)/[<b>choices</b>](choices) splits, as well as a repository for [<b>general</b>](general) atomic-resolution HAADF image simulation data with 
structure projection-based peak position suggestions.

## Where is the Data?

All folders in this repo are given as proxies to the full dataset hosted by the Materials Data Facility (MDF) and can be accessed by <<????>>. The folder structure of this repo is identical to the the folder structure present on MDF.

## Naming Conventions

All image simulation data entries (regardless of file format) are given a six-digit sequence representing the ICSD CollCode (zero-padded where appropriate), followed by a period, and another six-digit sequence which encodes the viewing angle (projection along a [u,v,w] direction). The first, third, and fifth positions of the second six-digit sequence encode the sign of the u,v,w index, respectively, with a 0 for a "+" integer, and a 1 for a "-" integer. The second, fourth, and sixth positions are the u,v,w indices themselves. For example, the sequence *011200* represents a uvw direction of [1,-2,0]. Note that some of the *png* images have additional tags which correspond to the distortion condition represented in the image. For this, naming is consistent with the descriptions in *Post-Processing Distortion Conditions*.


## Dataset #1: Image Retrieval

### Contents 
| Description                 |  Count  |
| --------------------------- | -------:|
| ICSD Structure Prototypes   |     600 |
| Oriented Supercells         |   2,400 |
| Distinct Images             |  16,000 |

Application of this dataset to image retrieval tasks can be found in:
* Schwenker, E. *et al.* [Image Matching for Computer Vision in Atomic-Resolution Electron Microscopy](http://example.com/ "Title"), *In progress* (2020)

### Structure Prototypes, Supercells, and Image Simulation
600 random (unique) structure prototypes from entries in the ICSD were rotated 4 times such that the resulting viewing angle coincided with a unique projection along a random integer combination [u,v,w] direction (integers are restricted to a range [-2,2]). The result is a collection of 2400 distinct oriented supercells (composition + viewing angle) with dimensions 25 x 25 x 25 Å. The chemistry of the structure prototypes, symmetry information, [uvw] viewing direction, associated CollCode from the ICSD - to name a few attributes - are summarized in the [**key.csv**](key.csv) file alongside additional citation information 

Each supercell is the input structure for a HAADF image simulation with [**PRISM**](http://prism-em.com/). Imaging noise (post-processed) and structural distortions are applied to the images/structures to produce an image sequence representing a space of reasonable noise conditions that correspond to distinct supercell created from an ICSD entry. Each image in a given sequence is sized at 256 x 256 and contains signal collected within a range of 100-150 mrad. Images printed to the *png* directories are 250 x 250 to minimize potential deleterious edge effects that arise from violation of structure periodicity assumptions at the boundary.

### Dataset Splits and Image Format
Standard image retrieval tasks involve searching for a relevant *targets* from an collections of image *choices*. As such, we have provided a division of the sythetic imaging data that is amenable to such a task, with a *targets* subset of the database images which are unique, but statistically similar to their corresponding *choices* pair. The *targets* split represents 400 unique oriented supercells postprocessed to emulate 16 distortion conditions (raw, clean, blur{1,2}, cnts{1,2}, scan{1,2}, bkgd{1,2}, dfct{1,2}, blbk{1,2}, comb{1,2}), for a total of **6400** images. The *choices* split contains 4 associated distortion types per image. There are 2400 unique oriented supercells (400 that are structural duplicates from *targets* set for matching tests) x 4 distortion conditions (raw, clean, blbk{1,2}), for a total of **9600** images in the *choices* split. The total number of images in the [<b>retrieval</b>](retrieval) dataset (across both splits) is **16,000**.

The above distortion conditions are described in more detail in the proceeding section. Separate  *png*  and *h5* (HDF5) directories are located within each of the datset splits to accomodate multiple data use cases. The *png* images are included for convenience as they represent a more viewing appropriate rescaling of the raw data. The *h5* images should be used for any comparison/matching tasks involving this dataset and contain additional attributes such as estimated peak position and chemistry information. Refer to <b>using_h5_data</b> Jupyter notebook for examples.

Note - these are not quantitatively accurate HAADF images, as structure periodicity assumptions at the boundary are violated throughout. To recreate these images in a more quantitatively accurate fashion, consult the publication and tutorials for the [**PRISM**](http://prism-em.com/) software. 

### Post-Processing Distortion Conditions
The approach for the creation of idealized STEM noise and distortions was originally developed by Colin Ophus in MATLAB. The [current version](files/addSTEMnoise.py) is available in python. Note that the input values given in the description of each distortion can be used as input to the function to replicate the specific noise condition when applied to the raw simulation output. A "1" or "2" appended to the distortion name (*see description of the h5 structure*) indicates the level of the given distortion. In all cases the greater number corresponds to a higher degree or amount of distortion.

| Distortion Name | Description                                                |  Input Values by Level (*[addSTEMnoise.py](files/addSTEMnoise.py)*) |
|-----------------|:-----------------------------------------------------------|-------------:|
|raw              |simulation output for pristine structure, no postprocessing | N/A |
|clean	  |trace amount of distortion (similar to a denoised experimental image) | [0.8,400,0.75,2] |
|blur	  |source size broadening effect with Gaussian blur            | **1:** [1.8,400,0.75,2], **2:** [2.8,400,0.75,2] |
|counts (cnts)	  |noise generated to capture Poisson characteristics of the signal | **1:** [0.8,100,0.75,2], **2:** [0.8,40,0.75,2] |
|scan	  |subpixel offset in x-direction to represent scanning noise  | **1:** [0.8,400,1.00,2], **2:** [0.8,400,1.25,2] |
|background (bkgd)	  |constant additive background (from long tails of STEM probe)| **1:** [0.8,400,0.75,6], **2:** [0.8,400,0.75,10] |
|defect (dfct)     |supercell w/ point defect in center of view, + cell relaxed locally defect | **1:** defect L1 + clean, **2:** defect L2 + clean | 
|blur/background (blbk)     |combination of blur and background conditions               | **1:** [1.8,400,1.00,6], **2:** [2.8,400,1.25,10] |
|combination (comb)     |combination of several of the underlying distortion conditions   | **1:** defect L1 + [1.8,100,1.00,6], **2:** defect L1 + [2.8,100,1.25,6] |


## Dataset #2: General Processed Simulation Output

### Contents 
| Description                 |  Count  |
| --------------------------- | -------:|
| ICSD Structure Prototypes   |   6,670 |
| Oriented Supercells         |  67,869 |
| Distinct Images             | 203,607 |

6670 random (unique) structure prototypes from entries in the ICSD were rotated a variable number of times, depending on the computed symmetry of structure, such that the resulting viewing angle coincided with a unique projection along a random integer combination [u,v,w] direction (integers are restricted to a range [-2,2]). The result is a collection of 67871 distinct oriented supercells (composition + viewing angle) with dimensions 25 x 25 x 25 Å. The entries in dataset #1 are a special futher-processed subset of the entries in this [<b>general</b>](general) dataset. Similar to dataset #1, the chemistry of the structure prototypes, symmetry information, [u,v,w] viewing direction, associated CollCode from the ICSD - to name a few attributes - are summarized in the [**key.csv**](key.csv) file alongside additional citation information, and each image that is formed from the raw data of the simulation is collected within a range of 100-150 mrad. With 67869 unique oriented supercells x 3 distortion conditions (raw, clean, blbk{1}), the total number of images in the [<b>general</b>](general) dataset is **203,607**.

Note - additional unique ICSD structure prototypes exist and will be added to to this general dataset periodically. For further questions or requests for access to raw MRC outputs from the PRISM simulations, contact [Eric Schwenker](eschwenk@u.northwestern.edu)


## Citing this dataset 

If you use this dataset or any of the associated functions in your research, we kindly ask that you cite: 
* Schwenker, E. *et al.* [Image Matching for Computer Vision in Atomic-Resolution Electron Microscopy](http://example.com/ "Title"), *In progress* (2020)
* Ophus, C. [A fast image simulation algorithm for scanning
transmission electron microscopy](https://link.springer.com/article/10.1186/s40679-017-0046-1), *Advanced Structural and
Chemical Imaging* 3(1), 13 (2017)
* Pryor Jr., A., Ophus, C. & Miao, J. [A streaming multi-GPU
 implementation of image simulation algorithms for scanning
 transmission electron microscopy](https://ascimaging.springeropen.com/articles/10.1186/s40679-017-0048-z), *Advanced Structural and
Chemical Imaging* 3, (2017)

