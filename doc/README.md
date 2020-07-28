# [DocGen Contest](https://dysdoc.github.io/docgen2/index.html)



## 比赛要求

1. 输入class qualifed name, 输出HTML格式的开发者文档
2. 生成的文档应回答如下问题
   1. 这个类是干什么的, 能解决什么样的问题
   2. 为什么这个类要这样实现
   3. 我应该如何使用这个类
3. 文档应包含如下内容:
   1. key method
   2. usage constraint
   3. usage example
   4. the role of the class in applicable design pattern
   5. known issues and limitation

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
- [ ] 这个类如何使用和被使用的 (蒙秀杰)
  - 如何使用使用这个类 - 类方法的return value为对应类名
  - 这个类如何被使用 - 类名作为方法的参数

### v1.4

- [ ] known issues and limitation (蒙秀杰)





