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
- [x] 返回方法注释的接口有问题
- [ ] 继承树展示只有extends没有implements (已反馈给佳展学长)
- [ ] 之后可以做的是为Type字段的内容加一个超链接，点击，直接打开一个新的界面，就是对应的类型的API文档。（其实就是打开一个新的界面，并且search的输入是对应的Type），所以后端返回的时候最好能返回type的全限定名，前端展示可以只展示权限定名的最后一截。
- [ ] 方法的详细信息表格，比照JDK文档，应该还有一种内容，说明当前方法抛出的异常和什么时候抛出异常。对应图里面的关系，应该是方法会有has exception condition这个关系，对应的实体就是描述什么时候会抛出什么类型的异常。对应的type字段是异常类的名字，name就是空，描述文本就是什么时候会抛异常。
- [x] 当前方法的声明，full declaration 在方法的名字下面可以展示。或者目前的方法的名字可以换成比如getFieldAsKeywords(Field field,Character keywordSeparator)这个换成声明信息量大些。
- [x] 比照JDK文档，应该有个地方是展示所有方法的表格，里面每个方法是表格一行，应该有三列：返回值类型，方法名字（带参数列表），方法的描述文本。
- [x] 样式问题，所有表格，标题，英语的习惯是每个词的首字母都大写，Method detail=> Method Detail. title=>Title. 
- [x] 相关概念是只有一个吗，相关概念应该展示多个，比如Top 5，或者Top 10
- [x] 在方法的详细信息界面，每个方法的描述文本应该还是要有的。
- [x] 每个类如果有描述文本应该也要展示，类的声明如果有的也可以展示，一些类的基础信息就可以展示在下面的很大的Tab前面。
- [ ] 因为field可能会有多个，是不是在下面的Basic Information同级的Tab会好些，比如有个Tab是Fields
- [ ] 可以添加一个Tab，名称为Constructors, 里面展示所有的构造方法，有一个所有构造方法的总表，和每个构造方法的详细描述。
- [ ] 目前的Basic Information改成Methods，里面展示所有的方法（可以是把构造方法排除掉的，当然目前不排除应该影响不大，只是一点显示优化，可以关注于先把更多信息展示到页面，目前样例代码在界面是看不到的）。
- [ ] 后端返回方法的列表的时候，可以按照权限定名简单排序一下，可能就没有那么乱了，python有个sorted方法 
- [ ] 点击对应Tab就触发刷新，而不是自己点击刷新按钮。
- [ ] 目前样例代码出来的都是只有一行的，可以都过滤掉？
- [ ] 每个方法的详细信息地方可能有地方显示这个方法的样例代码，可以先是点击按钮展示？
- [ ] 作为参数和作为返回值的每个其他方法，可以都同时附带一个样例代码，显示具体是如何使用的
- [ ] api方法和类分类后的label信息
- [ ] 图的可视化接口后端接口实现




## 可能可以添加的内容

1. deprecated API提取
2. 按字母构建索引 方法名字母序排列

   



## ToDo List

### v1.0


集成树后端接口：run.api_structure


- [x] 继承树 (刘阳)
  - extend (缺失用java.lang.Object)
  - implements 

- [x] 类下面的基本方法展示 (刘阳)
  - 类下面的方法展示, 参数, 返回值
  - 类下面的field
  - 类下面的constructor

### v1.1 

- [ ] [类的可视化图展示](http://bigcode.fudan.edu.cn/kg/index.html#/ElementGraph/890) (徐焕珺)

- [x] 相关概念 (刘阳)
  - 相关概念抽取
  - 最相关概念排序展示
- [ ] 相关概念组成的词云 
- [ ] 相关Wikidata概念。利用API比较的链接技术，对于API的相关概念，尝试链接到Wikidata，然后展示能链接上的wikidata概念（设置有超链接点击到wikidata概念页面和维基百科页面）

### v1.2

- [x] 将API类进行分类，比如实体类（表示了某个概念, 比如File），工具类(比如Util) (蒙秀杰)
  - [ ] 前端展示这个信息

- [x] 将API方法进行分类。比如属性操作方法（set，get方法），按照功能动词进行分类，比如都是append开头的方法 (蒙秀杰)
  - [ ] 前端展示

- [x] 类有的特性 (刘阳)
  - [ ] 前端展示
- [x] 类的概念分类 (is a, belong to) (刘阳)
  - [ ] 前端展示

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

