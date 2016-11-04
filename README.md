# DeepDrive setup

These instructions replicate the initial, all-Windows setup of DeepDrive. It is hacky, but it works. There is a parallel effort to integrate with OpenAI gym in which everything is much cleaner, but this is not in a publicly releasable state. If you’d like to contribute to this, get in touch at craig@deepdrive.com.

Also, this does not provide depth buffer extraction as a game update recently broke the way we hook the depth buffer. It should be a relatively simple fix though.

Here we go!

## Use the pre-built AMI (not recommended except as a reference install)
_Note that driving performance seems to be degraded due to possible latency and/or problems from an outdated cuda architecture. The car will still stay in the lane on this AMI like 50% of the time as opposed to 90% on a local install._

TODO: Add AMI's for every region here

Now skip to the [Running](#running) instructions

## Install from scratch 

This setup has been verified on Windows 7 Home, Windows 10 Home, and Windows 2012 Server on AWS.
We recommend a local setup with a GPU that supports [CUDA](http://hilinkit.appspot.com/yxjkh5) architecture 5.0 and at least 16GB of RAM.

### AMI setup
_If you want to run the environment on AWS, do the following first_
* Get [ec2gaming](http://lg.io/2015/07/05/revised-and-much-faster-run-your-own-highend-cloud-gaming-service-on-ec2.html) AMI - which has the video card driver and more properly configured
  * In the AWS web console, choose the AWS region [closest to you](http://www.cloudping.info/) using the top right dropdown
  * Then, in EC2, select launch instance. 
  * Under Community AMIs, search for *ec2gaming* and select one of the following:
```
ami-017dbf6a	(us-east)
ami-8735c5c3	(us-west-1)
ami-dfefeeef	(us-west-2)
ami-20175557	(eu-west-1)
ami-e47842f9	(eu-central-1)
ami-60cd6260	(ap-northeast-1)
ami-8c5b5bde	(ap-southeast-1)
ami-4d9eda77	(ap-southeast-2)
```
  * Choose the `g2.2xlarge` type in order to get the GPU required to run the game.
  * In step four _Add Storage_, make sure to change the EBS size from 35GB to 500GB (GTAV is around ~80GB and we want some extra room as well).
  * Don't worry about the keypair
  * Open a remote desktop or nomachine connection to the machine and login as `Administrator`, password `rRmbgYum8g`
  * Once you log in, you’ll be asked to change the Administrator password. If you’re on Windows, you’ll need to use a Mac or Linux or a mobile client to reset the password since there’s a bug in the Windows Remote Desktop client.
  * When you log in, search for *disk management* and open _Create and format hard disk partitions_
    * Right click the C:\ drive and extend it to the full 500GB

### Install requirements
--------------------
Open PowerShell (click the Start Menu in the bottom left and type "PowerShell", then right click and select "Run as Administrator")

HINT: To **Paste** commands into Powershell, make sure you don't have anything selected. Do this by pressing enter. Then, to paste, just right-click in Powershell (don't be a left clicker!).

Windows update - AMI only

Run Windows Update and restart if neccessary. It will stay at downloading 0kbps for a few minutes while it does some other CPU stuff. Don't worry, it will eventually start to actually download. The update takes several minutes, but you can continue to install things while the update takes place.

Allow Powershell to install things
```
Set-ExecutionPolicy RemoteSigned
```

Install [Chocolatey](https://chocolatey.org/install) to use as a Windows package manager.
```
iex ((new-object net.webclient).DownloadString('https://chocolatey.org/install.ps1'))
```

Restart PowerShell

Turn off UAC
```
C:\Windows\System32\cmd.exe /k %windir%\System32\reg.exe ADD HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v EnableLUA /t REG_DWORD /d 0 /f
```

Turn off IE ESC
```
REG ADD "HKLM\SOFTWARE\Microsoft\Active Setup\Installed Components\{A509B1A7-37E"
```

If windows update has not finished yet, it's probably a good idea to stop and wait for it. Once you've restarted, continue with the following:

Get Chrome (optional)
```
choco install googlechrome
```

Install requirements (one line at a time, or in different Powershell windows if you're impatient)
_Note what we're installing and omit things, like git, you may already have_
```
choco feature enable -n allowGlobalConfirmation
choco install python2
choco install git.install -yfd
choco install vcredist2013 vcredist2015
choco install autoit
```

Add AutoIt to your PATH

```
setx PATH "$env:path;C:\Program Files (x86)\AutoIt3\AutoItX" -m
```

Add Python to your PATH

```
setx PATH "$env:path;C:\tools\python2" -m
```

Install Vjoy

[Download the installer](https://drive.google.com/file/d/0B2UgaM91sqeAVE4wWWh3emFDbms/view) and run it. This is locked to a known working of version of vJoySetup.exe hosted in my Google Drive. You can install from vJoy's source forge if you're feeling [rebellious](https://sourceforge.net/projects/vjoystick/files/).

Add VJoy to your PATH

```
setx PATH "$env:path;C:\Program Files\vJoy\x86" -m
```

Restart PowerShell

Upgrade pip and add it to PATH by running the following (one line at a time)
```
python.exe -m pip install --upgrade pip
setx PATH "$env:path;C:\tools\python2\Scripts" -m
setx PYTHONPATH "C:\tools\python2;C:\tools\python2\Lib;C:\tools\python2\DLLs;C:\tools\python2\Lib\lib-tk;C:\Workspace\deepdrive" -m
```

Install [Cuda 7.5](https://developer.nvidia.com/cuda-75-downloads-archive) and verify the CUDA_PATH environment variable is pointing to 7.5.

(If you reinstall the graphics driver and are running in AWS, you may need to stop and start your instance)

Install the [directx sdk](https://www.microsoft.com/en-us/download/details.aspx?id=6812) - This allows displaying DirectX error messages. TODO: Make this optional.

Install the Windows SDK for your version of Windows
TODO: Make this optional

If you're running Windows 10, enable graphics features - http://stackoverflow.com/questions/32809169/use-d3d11-debug-layer-with-vs2013-on-windows-10 (TODO: Test for SdkLayersAvailable before adding D3D11_CREATE_DEVICE_DEBUG, so we don’t need this step)

Restart Windows

Get python scripts for installing and running the simulator

```
mkdir "C:\Program Files\DeepDrive"
cd "C:\Program Files\DeepDrive"
git clone https://github.com/crizcraig/deepdrive.git
cd deepdrive
pip install -r requirements.txt
```

Login automatically (AWS only) - Install and enter your password into [autologon](https://technet.microsoft.com/en-us/sysinternals/bb963905) to have the server logon on startup.

Install the Steam version of the game (the standalone version does not work on Windows Server 2012 as it's missing the necessary Windows Media Feature Pack). Otherwise the standalone version should work, and has the convenient `--offline` flag to keep the game from updating, but currently only the Steam version is tested.

Start the game, get to the screen that says "Story Mode" on the bottom right, then close the game. (This generates our saved games folder) TODO: Automate this

#### Set environment variable with GTAV directory

For the Steam version installed in C:\ use:
```
[Environment]::SetEnvironmentVariable("GTAV_DIR", "C:\Program Files (x86)\Steam\steamapps\common\Grand Theft Auto V", "User")
```

For the standalone version in C:\
```
[Environment]::SetEnvironmentVariable("GTAV_DIR", "C:\Program Files\Rockstar Games\Grand Theft Auto V", "User")
```

Run install.py
```
cd "C:\Program Files\DeepDrive\deepdrive"
python install.py
```

#### Xbox360ce setup
_Xbox360ce is a gamepad emulator that we will need in order to route control from vjoy to GTAV_
* Close GTAV if it's open
* Open x360ce_x64.exe in th GTAV folder and choose to create `xinput1_3.dll`
* Vjoy should then be automatically detected. Search for online settings and when it's done, click _Finish_
* Close xbox360ce
* Open the x360ce.ini and replace everything from `AxisToDPadDeadZone` down with [our config](https://gist.githubusercontent.com/crizCraig/f680f65653641412eba28c3c47421bcf/raw/4abd3be3802555f57d96389bf0a189dad8cd90de/x360ce.ini) 
* Save the file and reopen xbox360ce_x64.exe, your config should then look like this

![xbox360ce config](https://www.dropbox.com/s/5a2huyxdcby1qjz/Screenshot%202016-10-29%2014.59.17.png?dl=1)

* To test things out, open GTAV, the "Vjoy Feeder Demo", and repoen xbox360ce - Try sliding Axis X to steer the car and Axiz Z to control the car's throttle.
* Close "Vjoy Feeder Demo" and xbox360ce_x64.exe so that GTAVController.exe can take command of the virtual joystick device.
* Also, if you ever find that your mouse behaves strangely after running the simulator, open Vjoy Feeder Demo to reset the joystick controls

### GTAV Graphics settings
* Start GTA
* Hit Esc to enter the main menu -> Settings -> Graphics -> Pause Game On Focus Loss: Off
  * Ensure you're using directx 11
  * I use 800x600 resolution, but anything should work as it gets resized on the GPU to 227x227

### Start state
* Load Story Mode from the start screen of GTA
* You should see something similar to this
![deepdrive start](https://www.dropbox.com/s/5upus3x3r0ggiu8/Screenshot%202016-10-30%2014.22.11.png?dl=1)
* If you don't see the above car/location, then load the following saved game (this was downloaded into your saved games by install.py)
![deepdrive load](https://www.dropbox.com/s/kh9usuppivcmmid/Screenshot%202016-10-30%2014.21.24.png?dl=1)
* Now place the camera on the hood by hitting <kbd>v</kbd> until you see something like this
![deepdrive load](https://www.dropbox.com/s/q28tce40ukurm9p/Screenshot%202016-10-30%2014.33.50.png?dl=1)
* If you see the steering wheel, change the camera settings like so:
![deepdrive load](https://www.dropbox.com/s/h3xu98jz45bafld/Screenshot%202016-10-30%2014.28.42.png?dl=1)

### Setup OBS

* Run OBS.exe: `C:\Program Files\DeepDrive\OBS-new\rundir\OBS.exe`
* Add a new Game capture source

![add OBS game capture source](https://www.dropbox.com/s/kdimfv44oqfkweu/Screenshot%202016-10-30%2014.54.11.png?dl=1)

* Select the default options and hit OK

## Structure

The structure is ugly, and so is this diagram. Happy Haloween! ![deepdrive structure](https://www.dropbox.com/s/npum6771mcsuue8/DeepDrive-Structure.png?dl=1). 

# Running

```
cd "C:\Program Files\DeepDrive"
python run.py
```

## Passing caffemodel weights

```
python run.py --weights some.caffemodel
```

Where some.caffemodel is relative to `C:\Program Files\DeepDrive\caffe`

If you run into problems, it may be easier to see what the caffe process is doing by opening the `caffe.sln file` in Visual Studio and running (without building) from there. Check the output window for logs.

To save on CPU (esp. on AWS), you can close OBS once Game2Sensor is displaying the screen. This as OBS is only used to hook the frame buffer (see [Structure](#structure). 

If you're using the AWS AMI, be aware that the frames the neural net gets are somehow linked to what you see via RDP / nomachine. So if you see a low frame rate, the car is likely to drive off the road since the net is acting on outdated pixels. Also, the AWS g2 machines have old K520 NVidia card which use CUDA arch 3.0. I have a feeling this hurts performance as well, as the car drives off to the right and stalls out much more frequently than on a Win7 or Win10 machine I have with a GTX 980 and 1080 respectively. The net was trained on a GTX 980 with CUDA arch 5.0. So for the best performance, using a local windows machine with GPU that supports CUDA 5.0 is the way to go.

# Developing

Install Visual Studio Community 2013 (6GB) 
```
choco install visualstudiocommunity2013
```

Make sure any Nuget dependencies are downloaded by right clicking the Solution in the Solution Explorer and "Enable package restore"

If you see errors like
```
Error	4	error LNK1104: cannot open file 
```

Try opening Tools -> Nuget Package Manager -> Package Manager Console and hitting the `Restore` button in the banner that pops up in the console.


Install Boost

- Download 32 bit boost binaries from [here](https://sourceforge.net/projects/boost/files/boost-binaries/1.61.0/boost_1_61_0-msvc-12.0-32.exe/download)
- Set `BOOST_ROOT`
```
[Environment]::SetEnvironmentVariable("BOOST_ROOT", "C:\local\boost_1_61_0", "User")
```

## Making Windows nicer

I'd recommend installing a few things that will make development easier

```
choco install consolez github pycharm-community atom
```

[Resharper](https://www.jetbrains.com/resharper/download/) for Visual Studio is also highly recommended, although it's paid-only after 30 days.

## Packages

You can get installed packages with:
```
choco list -l
```
