# Document Generator
[![DOI](https://zenodo.org/badge/275757098.svg)](https://zenodo.org/badge/latestdoi/275757098)

This is a document generator backend which built by Flask. The goal is to build an automated system that can create on-demand developer documentation for a Java class.

## Getting Started

### Prerequisites

```
python==3.6.8
nltk==3.4.5
sekg==0.10.3.18
Flask==1.1.2
gunicorn==20.0.4
flask_cors==3.0.8
```

## Running the Service

You can simply typing the following command to start the service on server or localhost

```
gunicorn -b localhost:5000 run:app
```

## Authors

* Mingwei Liu
* Yang Liu
* Shuangshuang Xing
* Gang Lv
* Jiazhan Xie
* Huanjun Xu
* Xiujie Meng

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License.
