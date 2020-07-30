# [DocGen Contest](https://dysdoc.github.io/docgen2/index.html)

[toc]

## 比赛要求

1. 输入class qualifed name, 输出HTML格式的开发者文档
2. 生成的文档应回答如下问题
   1. 这个类是干什么的, 能解决什么样的问题 - what
   2. 为什么这个类要这样实现 - why
   3. 我应该如何使用这个类 - how
3. 文档应包含如下内容:
   1. key method
   2. usage constraint
   3. usage example
   4. the role of the class in applicable design pattern
   5. known issues and limitation



## 存在的问题

1. 方法的展示信息过于杂乱
   1. 方法参数的全限定名, 返回值的全限定名没有必要展示 (参考JDK文档)
   2. 方法参数:展示参数类型,参数名字,参数的描述文本
   3. 方法返回值: 返回值类型, 返回值描述文本

类里面每个方法的展示示例:

| 方法名       | 分类label | 描述信息                          |
| ------------ | --------- | --------------------------------- |
| parameter    | 类型 名称 | 描述文本(是不是不太需要描述文本?) |
| return value | 类型 名称 | 描述文本(是不是不太需要描述文本?) |

2. 返回方法注释的接口有问题
3. 继承树展示只有extends没有implements



## 可能可以添加的内容

1. deprecated API提取
2. 按字母构建索引 方法名字母序排列
3. 构造器方法与其他方法分开展示

4. 每个类的field信息展示
5. api方法和类分类后的label信息没有添加进去
6. 图的可视化接口后端接口实现



## ToDo List

### v1.0


集成树后端接口：run.api_structure


- [ ] 继承树 (刘阳)
  - extend (缺失用java.lang.Object)
  - implements 

- [ ] 类下面的基本方法展示 (刘阳)
  - 类下面的方法展示, 参数, 返回值
  - 类下面的field
  - 类下面的constructor

### v1.1 

- [ ] [类的可视化图展示](http://bigcode.fudan.edu.cn/kg/index.html#/ElementGraph/890) (徐焕珺)

- [ ] 相关概念 (刘阳)
  - 相关概念抽取
  - 最相关概念排序展示

### v1.2

- [x] 将API类进行分类，比如实体类（表示了某个概念, 比如File），工具类(比如Util) (蒙秀杰)

- [x] 将API方法进行分类。比如属性操作方法（set，get方法），按照功能动词进行分类，比如都是append开头的方法 (蒙秀杰)

- [ ] 类有的特性 (刘阳)

- [ ] 类的概念分类 (is a, belong to) (刘阳)

### v1.3

- [x] 关键方法排序(蒙秀杰)
  - pagerank算法
- [ ] 相关方法, 相关类展示 (蒙秀杰)
  - simrank算法
- [x] 方法的样例代码展示 (蒙秀杰)
  - 将抽取到的代码放到dc里
  - 利用文本匹配多行代码样例(参数申明)
- [x] 这个类如何使用和被使用的 (蒙秀杰)
  - 如何使用这个类 - 类方法的return value为对应类名
  - 这个类如何被使用 - 类名作为方法的参数

### v1.4

- [ ] known issues and limitation (蒙秀杰)

