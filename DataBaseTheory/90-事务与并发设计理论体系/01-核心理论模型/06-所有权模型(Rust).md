# 06 | 所有权模型 (Rust)

> **理论定位**: Rust所有权系统是编译期并发安全的核心机制，本文档提供从理论到实现的完整分析，并映射到LSEM L1层。

---

## 一、理论基础与动机

### 1.1 内存安全问题

**传统语言的困境** (C/C++):

| 问题类型 | 描述 | 后果 |
|---------|------|------|
| **悬垂指针** | 访问已释放内存 | 未定义行为、崩溃 |
| **二次释放** | 释放同一内存两次 | 堆损坏 |
| **数据竞争** | 多线程无同步访问 | 不确定结果 |
| **内存泄漏** | 忘记释放内存 | 资源耗尽 |

**传统解决方案的缺陷**:

- **垃圾回收** (Java/Go): 运行时开销、停顿
- **手动管理** (C/C++): 易错、难维护
- **运行时检查** (ThreadSanitizer): 性能损失、无法穷尽

### 1.2 Rust的创新

**核心思想**: 将内存安全**从运行时移到编译期**

$$\text{Memory Safety} = \text{Compile-time Proof} \implies \text{Zero Runtime Cost}$$

**关键机制**:

1. **所有权系统** (Ownership): 管理资源生命周期
2. **借用检查器** (Borrow Checker): 验证引用有效性
3. **生命周期** (Lifetime): 追踪引用时长

---

## 二、所有权系统

### 2.1 三大规则

**规则1 (唯一所有者)**:

$$\forall v \in Values: \exists! owner: Owns(owner, v)$$

每个值有且仅有一个所有者。

**规则2 (所有权转移)**:

$$Move(v, owner_1 \to owner_2) \implies \neg Access(owner_1, v)$$

所有权转移后，原所有者失去访问权。

**规则3 (作用域释放)**:

$$owner \text{ out of scope} \implies Drop(v)$$

所有者离开作用域时，自动释放资源。

### 2.2 形式化定义

**定义2.1 (所有权状态)**:

$$OwnershipState = (Value, Owner, Scope)$$

**状态转换函数**:

$$\delta: OwnershipState \times Action \rightarrow OwnershipState$$

**动作类型**:

| 动作 | 语义 | 状态变化 |
|-----|------|---------|
| **Create** | `let x = value;` | $(v, x, scope_x)$ |
| **Move** | `let y = x;` | $(v, x, s_x) \to (v, y, s_y)$ |
| **Drop** | 作用域结束 | $(v, x, s_x) \to \emptyset$ |
| **Borrow** | `let r = &x;` | 创建临时引用（不转移所有权） |

### 2.3 代码示例与分析

#### 示例1: 基本所有权

```rust
fn ownership_transfer() {
    let s1 = String::from("hello");  // s1拥有字符串

    let s2 = s1;  // 所有权转移到s2

    // println!("{}", s1);  // ❌ 编译错误: s1不再有效
    println!("{}", s2);     // ✅ s2有效
}  // s2离开作用域，字符串被释放
```

**状态演化**:

```
初始: ∅
    ↓ let s1 = ...
状态1: (String("hello"), s1, scope_fn)
    ↓ let s2 = s1
状态2: (String("hello"), s2, scope_fn)  [s1失效]
    ↓ 函数结束
状态3: ∅  [自动释放]
```

#### 示例2: 函数传参

```rust
fn takes_ownership(s: String) {  // s获得所有权
    println!("{}", s);
}  // s离开作用域，String被释放

fn main() {
    let s = String::from("hello");

    takes_ownership(s);  // 所有权转移到函数

    // println!("{}", s);  // ❌ 编译错误: s已失效
}
```

#### 示例3: Clone vs Move

```rust
fn clone_vs_move() {
    let s1 = String::from("hello");

    // Move: 转移所有权
    let s2 = s1;  // s1失效

    // Clone: 深拷贝
    let s3 = s2.clone();  // s2仍然有效

    println!("{}, {}", s2, s3);  // ✅ 都有效
}
```

---

## 三、借用系统

### 3.1 借用规则

**规则4 (不可变借用)**:

$$\forall v: \exists \{&v_1, &v_2, ..., &v_n\} \text{ 同时存在}$$

可以有多个不可变引用同时存在。

**规则5 (可变借用唯一性)**:

$$\forall v: \exists \&\text{mut } v \implies \neg\exists \text{other references}$$

可变引用是唯一的，与任何其他引用互斥。

**规则6 (借用作用域)**:

$$\forall \&v: Lifetime(\&v) \subseteq Lifetime(owner(v))$$

引用的生命周期不能超过所有者。

### 3.2 形式化定义

**定义3.1 (引用状态)**:

$$ReferenceState = (Value, RefType, Lifetime)$$

其中:

$$RefType \in \{\&T, \&\text{mut } T\}$$

**借用检查函数**:

$$BorrowCheck: \text{Program} \rightarrow \{\text{Valid}, \text{Error}\}$$

**冲突矩阵**:

| 已存在 \ 新建 | &T (不可变) | &mut T (可变) |
|-------------|------------|--------------|
| **无引用** | ✅ | ✅ |
| **&T** | ✅ (多个不可变) | ❌ 冲突 |
| **&mut T** | ❌ 冲突 | ❌ 冲突 |

### 3.3 代码示例与分析

#### 示例4: 不可变借用

```rust
fn immutable_borrows() {
    let s = String::from("hello");

    let r1 = &s;  // ✅ 不可变借用
    let r2 = &s;  // ✅ 可以多个
    let r3 = &s;  // ✅ 继续借用

    println!("{}, {}, {}", r1, r2, r3);  // 都有效

    println!("{}", s);  // ✅ 所有者仍可访问（只读）
}
```

**借用图**:

```
    s (owner)
    ↓ 借用
    ├─→ r1: &String
    ├─→ r2: &String
    └─→ r3: &String

    所有引用只读，互不干扰
```

#### 示例5: 可变借用

```rust
fn mutable_borrow() {
    let mut s = String::from("hello");

    let r1 = &mut s;  // ✅ 可变借用
    r1.push_str(", world");

    // let r2 = &s;     // ❌ 编译错误: 可变借用期间不能有不可变借用
    // let r3 = &mut s; // ❌ 编译错误: 只能有一个可变借用

    println!("{}", r1);  // ✅ r1有效

    // r1离开作用域后
    println!("{}", s);  // ✅ 所有者可再次访问
}
```

#### 示例6: 借用作用域

```rust
fn borrow_scope() {
    let mut s = String::from("hello");

    {
        let r1 = &mut s;
        r1.push_str(", world");
    }  // r1离开作用域

    let r2 = &s;  // ✅ 现在可以借用了
    println!("{}", r2);
}
```

**关键**: **非词法作用域生命周期** (NLL, Non-Lexical Lifetimes)

编译器分析引用的**实际使用范围**，而不是词法作用域：

```rust
fn nll_example() {
    let mut s = String::from("hello");

    let r1 = &s;
    println!("{}", r1);  // r1最后一次使用
    // r1实际生命周期到此结束（NLL优化）

    let r2 = &mut s;  // ✅ 允许，因为r1已不再使用
    r2.push_str(", world");
}
```

---

## 四、生命周期系统

### 4.1 生命周期标记

**定义4.1 (生命周期)**:

$$Lifetime = \text{Scope in which reference is valid}$$

**符号**: `'a`, `'b`, `'static`, ...

**语法**:

```rust
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() {
        x
    } else {
        y
    }
}
```

**语义**: 返回值的生命周期至少与输入参数中最短的生命周期一样长

### 4.2 生命周期推导规则

**规则7 (输入生命周期)**:

$$\forall \text{input ref}: \text{distinct lifetime}$$

```rust
fn foo(x: &i32, y: &i32) {
    // 推导为: fn foo<'a, 'b>(x: &'a i32, y: &'b i32)
}
```

**规则8 (输出生命周期)**:

$$\text{Single input} \implies \text{output lifetime} = \text{input lifetime}$$

```rust
fn first(x: &str) -> &str {
    // 推导为: fn first<'a>(x: &'a str) -> &'a str
    x
}
```

**规则9 (方法self生命周期)**:

$$\text{Method with } \&self \implies \text{output lifetime} = '\text{self}$$

```rust
impl MyStruct {
    fn get_data(&self) -> &String {
        // 推导为: fn get_data<'a>(&'a self) -> &'a String
        &self.data
    }
}
```

### 4.3 生命周期约束

**子类型关系**:

$$'a: 'b \quad \text{means } 'a \text{ outlives } 'b$$

```rust
fn subtype<'a: 'b, 'b>(x: &'a i32) -> &'b i32 {
    x  // ✅ 'a活得更久，可以转换为'b
}
```

**形式化**:

$$Lifetime_1 \subseteq Lifetime_2 \implies 'lifetime_1: 'lifetime_2$$

---

## 五、并发原语

### 5.1 Send与Sync Trait

**定义5.1 (Send trait)**:

$$Send: \text{Type can be transferred across thread boundaries}$$

```rust
trait Send {}

// 自动实现
impl Send for i32 {}
impl<T: Send> Send for Vec<T> {}

// 不实现（线程不安全）
impl !Send for Rc<T> {}  // 引用计数非原子
```

**定义5.2 (Sync trait)**:

$$Sync: \&T \text{ is Send} \iff T \text{ is Sync}$$

```rust
trait Sync {}

// 自动实现
impl Sync for i32 {}
impl<T: Sync> Sync for Arc<T> {}

// 不实现
impl !Sync for Cell<T> {}  // 内部可变性非线程安全
```

**定理5.1 (并发安全)**:

$$\forall T: (T: Send \land T: Sync) \implies \text{ThreadSafe}(T)$$

**证明**: 见 `03-证明与形式化/04-所有权安全性证明.md#定理5.1`

### 5.2 Arc与Mutex

**Arc (Atomic Reference Counting)**:

```rust
use std::sync::Arc;

fn arc_example() {
    let data = Arc::new(vec![1, 2, 3]);

    let data_clone1 = Arc::clone(&data);  // 引用计数+1
    let data_clone2 = Arc::clone(&data);  // 引用计数+1

    let handle1 = thread::spawn(move || {
        println!("{:?}", data_clone1);  // 线程1拥有一个引用
    });

    let handle2 = thread::spawn(move || {
        println!("{:?}", data_clone2);  // 线程2拥有另一个引用
    });

    handle1.join().unwrap();
    handle2.join().unwrap();

    println!("{:?}", data);  // 主线程仍有引用
}  // 所有引用离开作用域，data被释放
```

**内部实现**:

```rust
struct Arc<T> {
    ptr: *const ArcInner<T>,  // 指向堆的指针
}

struct ArcInner<T> {
    strong: AtomicUsize,  // 原子引用计数
    data: T,
}

impl<T> Clone for Arc<T> {
    fn clone(&self) -> Arc<T> {
        // 原子递增
        self.inner().strong.fetch_add(1, Ordering::Relaxed);
        Arc { ptr: self.ptr }
    }
}

impl<T> Drop for Arc<T> {
    fn drop(&mut self) {
        // 原子递减
        if self.inner().strong.fetch_sub(1, Ordering::Release) == 1 {
            // 最后一个引用，释放内存
            unsafe { drop_in_place(self.ptr) }
        }
    }
}
```

**Mutex (互斥锁)**:

```rust
use std::sync::{Arc, Mutex};

fn mutex_example() {
    let counter = Arc::new(Mutex::new(0));

    let mut handles = vec![];

    for _ in 0..10 {
        let counter_clone = Arc::clone(&counter);

        let handle = thread::spawn(move || {
            let mut num = counter_clone.lock().unwrap();
            *num += 1;
        });  // num离开作用域，自动解锁

        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    println!("Result: {}", *counter.lock().unwrap());  // 10
}
```

**RAII模式**:

$$Lock \implies Guard \xrightarrow{drop} Unlock$$

```rust
impl<T> MutexGuard<'_, T> {
    // Drop trait自动实现
    fn drop(&mut self) {
        // 自动释放锁
        self.inner.unlock();
    }
}
```

### 5.3 RwLock (读写锁)

**规则**: 多读者单写者

$$\exists \&\text{mut } T \implies \neg\exists \text{any other reference}$$

$$\exists \{&T_1, ..., &T_n\} \implies \neg\exists \&\text{mut } T$$

```rust
use std::sync::RwLock;

fn rwlock_example() {
    let data = RwLock::new(vec![1, 2, 3]);

    // 多个读者可以并发
    {
        let r1 = data.read().unwrap();
        let r2 = data.read().unwrap();
        println!("{:?}, {:?}", r1, r2);
    }  // 读锁释放

    // 唯一写者
    {
        let mut w = data.write().unwrap();
        w.push(4);
    }  // 写锁释放
}
```

**性能对比**:

| 操作 | Mutex | RwLock (无竞争) | RwLock (有竞争) |
|-----|-------|----------------|----------------|
| 读操作 | 50ns | 30ns | 100ns (等待写者) |
| 写操作 | 50ns | 50ns | 500ns (等待读者) |

---

## 六、内存排序

### 6.1 原子类型

**定义6.1 (原子操作)**:

$$Atomic: \text{Operation that appears to occur instantaneously}$$

**类型**:

```rust
use std::sync::atomic::*;

AtomicBool
AtomicI8, AtomicI16, AtomicI32, AtomicI64, AtomicIsize
AtomicU8, AtomicU16, AtomicU32, AtomicU64, AtomicUsize
AtomicPtr<T>
```

### 6.2 内存排序

**定义6.2 (happens-before关系)**:

$$e_1 \xrightarrow{hb} e_2 \iff e_1 \text{ is visible to } e_2$$

**Ordering类型**:

| Ordering | 保证 | 性能 | 使用场景 |
|----------|------|------|---------|
| **Relaxed** | 仅原子性 | 最高 | 简单计数器 |
| **Acquire** | 读同步点 | 中 | 锁获取 |
| **Release** | 写同步点 | 中 | 锁释放 |
| **AcqRel** | 读写同步 | 中 | CAS |
| **SeqCst** | 全局顺序 | 最低 | 严格同步 |

### 6.3 Release-Acquire示例

```rust
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};

static FLAG: AtomicBool = AtomicBool::new(false);
static DATA: AtomicU64 = AtomicU64::new(0);

// 线程1: 写入数据并设置标志
fn thread1() {
    DATA.store(42, Ordering::Relaxed);  // 写数据
    FLAG.store(true, Ordering::Release);  // ← 同步点
}

// 线程2: 等待标志并读取数据
fn thread2() {
    while !FLAG.load(Ordering::Acquire) {  // ← 同步点
        // 等待
    }

    let value = DATA.load(Ordering::Relaxed);  // 读数据
    println!("{}", value);  // 保证看到42
}
```

**happens-before关系**:

$$\text{store}(\text{Release}) \xrightarrow{hb} \text{load}(\text{Acquire})$$

**保证**: Acquire之前的所有Release操作都可见

---

## 七、与LSEM L1层的映射

### 7.1 状态空间映射

| LSEM L1 | Rust所有权 |
|---------|-----------|
| **状态单元** | 堆/栈内存位置 |
| **时空戳** | 生命周期'a + Ordering |
| **可见性算法** | 借用检查器 |
| **冲突仲裁** | 编译期拒绝 + 运行时锁 |

### 7.2 可见性映射

**L1可见性规则** (LSEM):

$$Visible_{L1}(ref, lifetime, observer) \iff$$
$$lifetime_{ref} \subseteq lifetime_{owner} \land \text{BorrowCheck}(\text{refs})$$

**Rust实现**:

```rust
fn visible_l1<'a, T>(reference: &'a T, observer: &'a Processor) -> bool {
    // 编译器保证:
    // 1. 生命周期'a有效
    // 2. 借用规则满足
    // 3. 无数据竞争

    true  // 编译通过即可见
}
```

### 7.3 冲突检测映射

**L1冲突矩阵**:

| 操作类型 | 读(&T) | 写(&mut T) |
|---------|--------|-----------|
| **读(&T)** | ✓ | ✗ |
| **写(&mut T)** | ✗ | ✗ |

**对应L0**:

| 操作类型 | SELECT | UPDATE |
|---------|--------|--------|
| **SELECT** | ✓ (MVCC) | ✓ (MVCC) |
| **UPDATE** | ✓ (MVCC) | ✗ (锁) |

**关键差异**: Rust在**编译期**检测，PostgreSQL在**运行时**检测

---

## 八、与其他语言对比

### 8.1 Rust vs C++

| 维度 | Rust | C++ |
|-----|------|-----|
| **内存安全** | 编译期保证 | 运行时检查（可选） |
| **并发安全** | 借用检查器 | ThreadSanitizer（运行时） |
| **性能开销** | 零 | 工具开销20-50% |
| **学习曲线** | 陡峭（新概念） | 平缓（但易错） |
| **灵活性** | 受限（安全优先） | 高（程序员负责） |

### 8.2 Rust vs Java/Go

| 维度 | Rust | Java/Go |
|-----|------|---------|
| **内存管理** | 编译期RAII | GC垃圾回收 |
| **并发模型** | 所有权+锁 | 锁+通道 |
| **性能** | 接近C/C++ | 中等 |
| **停顿** | 无GC停顿 | GC停顿（ms级） |
| **内存占用** | 低（无GC开销） | 高（GC元数据） |

---

## 九、实践模式

### 9.1 共享状态并发

**模式**: `Arc<Mutex<T>>`

```rust
use std::sync::{Arc, Mutex};

struct Database {
    connection_pool: Arc<Mutex<Vec<Connection>>>,
}

impl Database {
    pub fn get_connection(&self) -> Connection {
        let mut pool = self.connection_pool.lock().unwrap();
        pool.pop().unwrap()
    }

    pub fn return_connection(&self, conn: Connection) {
        let mut pool = self.connection_pool.lock().unwrap();
        pool.push(conn);
    }
}
```

### 9.2 消息传递并发

**模式**: `mpsc::channel`

```rust
use std::sync::mpsc;
use std::thread;

fn message_passing() {
    let (tx, rx) = mpsc::channel();

    thread::spawn(move || {
        tx.send(String::from("hello")).unwrap();
    });

    let received = rx.recv().unwrap();
    println!("{}", received);
}
```

**优势**: 避免共享状态，降低锁竞争

### 9.3 异步编程

**Tokio异步运行时**:

```rust
use tokio::sync::RwLock;

#[tokio::main]
async fn main() {
    let data = Arc::new(RwLock::new(vec![1, 2, 3]));

    let data_clone = Arc::clone(&data);

    let handle = tokio::spawn(async move {
        let read_guard = data_clone.read().await;
        println!("{:?}", *read_guard);
    });

    {
        let mut write_guard = data.write().await;
        write_guard.push(4);
    }

    handle.await.unwrap();
}
```

**异步借用规则**: 与同步借用规则相同，但在`.await`点检查

---

## 十、总结

### 10.1 核心贡献

**理论贡献**:

1. **所有权形式化定义**（第二章）
2. **借用检查算法**（第三章）
3. **生命周期系统**（第四章）
4. **与LSEM L1层映射**（第七章）

**工程价值**:

1. **编译期保证**: 零运行时开销
2. **RAII模式**: 自动资源管理
3. **并发安全**: 类型系统证明

### 10.2 关键公式

**所有权不变式**:

$$\forall v: |\{owner: Owns(owner, v)\}| = 1$$

**借用冲突**:

$$(\exists \&\text{mut } T) \implies (\neg\exists \&T \land \neg\exists \&\text{mut } T')$$

**生命周期偏序**:

$$'a: 'b \iff Scope('a) \supseteq Scope('b)$$

### 10.3 设计原则

1. **所有权优先**: 能用所有权就不用借用
2. **借用最小化**: 引用作用域尽可能短
3. **Arc谨慎使用**: 引用计数有开销
4. **锁粒度控制**: 临界区尽可能小

---

## 十一、延伸阅读

**理论基础**:

- *The Rust Programming Language* (Steve Klabnik & Carol Nichols)
- Rust Nomicon (高级内存安全话题)
- Rust RFC 2094 (NLL非词法生命周期)

**实现细节**:

- Rust编译器源码: `compiler/rustc_borrowck/`
- 借用检查算法: Polonius项目
- 内存模型规范: Rust Memory Model Working Group

**扩展方向**:

- `01-核心理论模型/07-内存模型与排序.md` → happens-before详解
- `03-证明与形式化/04-所有权安全性证明.md` → 完整数学证明
- `05-实现机制/04-Rust-所有权实现.md` → 编译器实现

---

**版本**: 1.0.0
**最后更新**: 2025-12-05
**关联文档**:

- `01-核心理论模型/01-分层状态演化模型(LSEM).md`
- `01-核心理论模型/07-内存模型与排序.md`
- `05-实现机制/04-Rust-所有权实现.md`
