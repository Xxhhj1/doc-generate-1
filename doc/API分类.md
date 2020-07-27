# API分类

## API方法分类 - 10350

- accessor - 5329
  - get方法
  - predict方法: 通过对local field进行判断, 返回boolean类型
  - void-accessor: 通过参数返回local field信息
- mutator - 2221
  - set方法
  - controller方法: 通通过调用内部和外部方法来提供控制逻辑
- creational - 156
  - copy方法: 拷贝对象
  - factory方法: 实例化一个对象然后返回
- constructor - 1120
- undefined - 1524
  - abstract方法
  - empty方法
  - incidental: 除以上各例外的其他方法

## API类的分类 - 1474

- Entity类: encapsulates data and behavior - 1162
  - |accessor method| + |mutator method|占方法总数的80%以上
- Factory类: consists most of the factory methods - 6
  - creational method占方法总数的50%以上
- Util类: 工具类 - 126
  - |mutator method| > |accessor method|

- Pool类: consists mostly of class constants and a few or no methods - 169
- Undefined类: 除以上各例外的其他类 - 11