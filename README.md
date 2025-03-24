# rgb_to_reflectance_qgis
QGIS plugin to convert RGB values from Micasense imagery to reflectance values


# Important Note
This QGIS plugin is still under experimental development and testing, as a result it is not unlikely that errors may occur when trying to install or run the plugin. Please feel free to report any errors on the issues page. So far, it has been tested on the following platforms and versions:
|Platform|QGIS Version|Python version|
|:---|:---|:---|
|Linux (Ubuntu) | 3.26.3 | 3.9 |
|Windows 11 | 3.32.3 | 3.9 |

## Installation

### Prerequisites
Windows: You will need at least QGIS version 3.26  
Mac and Linux: You will need to have Python >= 3.9 on your system and in the PATH, and at least QGIS version 3.26

### Download the zip file
Download the rgb_to_reflectance.zip file in this repository.

### Instalation in Quantum GIS
In QGIS, go to the plugins menu, select 'Manage and Install Plugins', then go to 'Install from ZIP'. 

![409284208-cc7cd9b3-e39d-497a-a7a1-ea2a9c0eaba9](https://github.com/user-attachments/assets/16eea8e6-6928-48f1-831f-ecbbef116f88)

Here, select the zip file you downloaded and click 'Install Plugin'. You will get a security warning about installing plugins from "untrusted sources". You can click "Yes" to continue with the installation process.

![409285614-b6d5a164-9cf1-463f-a00e-7cfda87e7b25](https://github.com/user-attachments/assets/c05d0d76-b406-4023-a9c7-83b284a8bff4)

Once it has finished, go to the 'Installed' tab, and uncheck and recheck the checkbox for the RGB to Reflectance plugin.

There may be delay as the package runs some installation steps, which may take a few minutes.

You are done!

## Usage
To use, open the plugin and select your input folder. Then click 'run'. Outputs will be created in a new folder adjacent to your input folder, named `<input_folder_name>_reflectance`. It will run in the background until finished, at which point the progress bar will reach 100%. That's all there is to it.
