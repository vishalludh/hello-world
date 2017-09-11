=[SYNOPSIS]=============================================================
Code in this directory will build the Docker image for UNIFI MOD1. Such 
Docker image will be conform to the TA2 API - see 
https://mediforprogram.com/wiki/display/MEDIFOR/TA2+API+Tutorial+Series
for detailed intruction for Docker image building.
Specific command to be used for UNIFI MOD1 will be discussed in the 
Installation Section.
Documentation specifically related to the UNIFI MO1 can be found in the 
Integrity_Indicator/docs folder of this package.

=[INPUTS/OUTPUTS]=======================================================
The submitted implementation of MOD1 requires a single image as input, 
while in outputs it returns an IntegrityScore and the position of the
estimated image Pricipal Point (PP).

JSON formatted input should be a follows:

{
  "image": {"$resource": "image"}
}

JSON formatted output is:

{
  "algorithm": {
    "algotithm_type": "physical",
    "description": "Cropping detection based on Principal Point",
    "manipulations_detected": "crop",
    "media_type": "image",
    "name": "unifi_mod1",
    "version": "1.0"
  },
  "detections": {
    "confidence": <confidence score>,
    "manip_description": "cropping detection based on PP estimation",
    "manip_explanation": "Image PP fall away from the image center",
    "manip_name": "crop",
    "specificity": "global"
  },
  "estimated_properties": {
    "description": "Position of the image pricipal point",
    "name": "Principal Point coordinate",
    "value": {
      "xval": <X-Coordinate of PP w.r.t image coordinate system>,
      "yval": <Y-Coordinate of PP w.r.t image coordinate system>
    }
  },
  "is_manipulated": "true/false",
  "no_prediction": "true/false"
}

Note that, no localization map is produced in output.

=[DOCUMENTATION]========================================================
Documentation specifically related to the UNIFI MO1 can be found in the 
Integrity_Indicator/docs folder of this package.
Specific command to be build the UNIFI MOD1 Docker image, will be 
discussed in the Installation Section.

=[PREREQUISITE]=========================================================
In order to build the UNIFI MOD1 Docker image, it is required:

- Matlab R2016b, with the Matlab Compiler SDK
- Medifor TA2 API (gitlab.mediforprogram.com/sri/medifor.git), already 
  included in this packagehuawey p9 lite 
- Other requirements can be found in the Integrity_Indicator/README.txt, 
  in the Prerequisites Section
  
=[INSTALLATION]=========================================================
If all the prerequisites are satisfied, the UNIFI MOD1 Docker image
should be build the the following comand. From the Integrity_Indicator/
folder type

> cd medifor
> docker build -t unifi-mod1 .

This comand will call the Dockerfile used to build the app.

Hereafter, we report the full instruction pipeline. Note that, we 
suppose that the UNIFI MOD1 is already able to run on the host machine
(i.e. all the Prerequisites specified in Integrity_Indicator/README.txt 
are already satisfied.

Setup the machine

> cd Integrity_Integration/
> sudo apt-get install python3-venv libjpeg-dev zlib1g-dev

Get the TA2 API code. While in the Integrity_Integration folder,

> git clone --branch 1.1.2 https://gitlab.mediforprogram.com/sri/medifor.git temp
> mv temp/* medifor/
> rm -rf temp
> cd medifor

Setup virtualenv (venv)

> python3.5 -m venv venv 
> source venv/bin/activate
> pip install --upgrade pip

Install medifor API

> pip install --requirement medifor/requirements.txt
> python medifor/setup.py install

Install TA2 tutorial

> pip install --requirement tutorial/sequential_processing/requirements.txt
> python tutorial/sequential_processing/setup.py install

Install and setup Docker (see MODULE_2, Section 1 of the TA2 Tutorial at 
https://mediforprogram.com/wiki/display/MEDIFOR/2+-+Running+an+Algorithm+with+Docker)

Build the medifor Docker image

> ln -sf docker/medifor/Dockerfile Dockerfile
> docker build -t medifor .

Build the medifor-matlab Docker image

> ln -sf docker/medifor-matlab/Dockerfile Dockerfile
> docker build -t medifor-matlab .

Build the UNIFI MOD1 lib and produce the related Dockerfile. To do so, 
modify the bms file adding after line #164 
"flist += glob.glob('./**/*.mexa64', recursive=True)" the following two 
lines to include *.a and *.so libraries

    flist += glob.glob('./**/*.a', recursive=True)
    flist += glob.glob('./**/*.so', recursive=True)
    
Then run the following comand

> ./medifor/matlab/bms mod1 MOD1 --docker

where "mod1" is the project name, and MOD1 the folder containing the 
code together with the service_properties.m and process_run.m files. The 
"--docker" option is used to create the Dockerfile. NOTE: before compile
again mod1 with the bms, delete the /medifor/MOD1/build folder

Modify the generated Dockerfile (i.e., MOD1/Dockerfile) and change the
following lines

- line #2: change "FROM medifor-matlab:R2016b" to "FROM medifor-matlab"
- after line #5 "ADD MOD1 /medifor/MOD1" add the following two lines 
	ADD /MOD1/code/libs/LIBS/liblapack.so /usr/lib/liblapack.so.3
	ADD /MOD1/code/libs/LIBS/libblas.so /usr/lib/libblas.so.3

RUN rm build/CMakeCache.txt && \
    /medifor/medifor/matlab/bms mod1 --build wrapper --nopre --mlab R2016b
    
with 

RUN rm build/CMakeCache.txt && \
    apt-get install -y liblapack3 minpack-dev && \
    /medifor/medifor/matlab/bms mod1 --build wrapper --nopre --mlab R2016b

to include in the Docker image the required dependencies.

Now build the unifi-mod1 Docker image with

> ln -sf MOD1/Dockerfile Dockerfile
> docker build -t unifi-mod1 .

=[TEST]=================================================================
To run and test the unifi-mod1 Docker image, at first run it with

> docker run -p 5000:80 unifi-mod1

Then, on a different console window, run the MOD1/test.py with

> python MOD1/test.py http://localhost:5000/

This test will load two sample image and send them to the unifi-mod1 
service. Image will be then precessed by unifi-mod1 and an output JSON
will be sent back to the test app (and visualized on the web page
http://localhost:5000.




