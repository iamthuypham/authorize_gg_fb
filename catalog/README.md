# Catalog Item App
### Requirement
1. Oracle VM Virtual Box
Version 5.1.22 r115126 (Qt5.6.2) was used for this application.

2. Vagrant
Version 1.8.5 was used for this application.

3. Git Bash

### Install
1. Install Oracle VM Virtual Box
2. Install Vagrant
3. Download the zip folder
4. Unzip

### Start the app
1. Open Git Bash
2. Change directory to the vagrant folder location
3. Run vagrant using 
```
vagrant_up
```
**Note:** This step will take approx. 5 min
4. Log in vagrant
```
vagrant ssh
```
5. Change directory to vagrant folder
```
cd /vagrant
```

6. Change directory to the catalog folder

```
cd catalog
```
7. Run project.py
```
python project.py
```