# API方法分类

- accessor
  - get方法
  - predict方法: 通过对local field进行判断, 返回boolean类型
  - void-accessor: 通过参数返回local field信息
- mutator
  - set方法
  - controller方法: 通通过调用内部和外部方法来提供控制逻辑
- creational
  - constructor
  - copy方法: 拷贝对象
  - factory方法: 实例化一个对象然后返回
- degenerate
  - abstract方法
  - empty方法
  - incidental: 除以上各例外的其他方法