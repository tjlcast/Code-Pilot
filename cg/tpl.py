#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time 2024/1/20 12:46
# @Name. Py
# @Author: jialtang

# application 配置示例
applicationYml = """
spring:
  datasource:
    url: jdbc:mysql://aigcdb:3306/llmdb_dev?useSSL=false&useUnicode=true&characterEncoding=UTF-8&serverTimezone=Asia/Shanghai&allowMultiQueries=true
    username: root
    password: root1234
    driver-class-name: com.mysql.cj.jdbc.Driver

    hikari:
      minimumIdle: 10
      maximumPoolSize: 50
      connectionTestQuery: SELECT 1
      poolName: hikariCadp
      connectionTimeout: 60000
      idleTimeout: 50000
      maxLifetime: 54000

"""


# maven 示例
mavenPom = """

    <properties>
        <maven.compiler.source>8</maven.compiler.source>
        <maven.compiler.target>8</maven.compiler.target>
    </properties>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.3.5.RELEASE</version>
        <relativePath/>
    </parent>

    <dependencies>
        <!--   SpringBoot base     -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- MySQL JDBC Driver -->
        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
        </dependency>
        <dependency>
            <groupId>com.baomidou</groupId>
            <artifactId>mybatis-plus-boot-starter</artifactId>
            <version>3.4.2</version>
        </dependency>

        <!--    utils    -->
        <dependency>
            <groupId>org.apache.commons</groupId>
            <artifactId>commons-lang3</artifactId>
            <version>3.2</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <version>2.7.10</version>
                <configuration>
                    <mainClass>com.hzbank.chatbi.Run</mainClass>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <configuration>
                    <source>8</source>
                    <target>8</target>
                </configuration>
            </plugin>
        </plugins>
    </build>

"""


# 示例JSON数据
entity = """

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;

public class {{ ctx.entity.name }} {

    {% for field in ctx.entity.fields %}
    {% if field.name=='id' %}@TableId(value = "{{field.name|to_snake_case}}", type = IdType.AUTO){% else %}@TableField("{{field.name|to_snake_case}}"){% endif %}
    private {{field.type}} {{field.name | lower_camel_case}};
    {% endfor %}
    
    {% for field in ctx.entity.fields %}
    public {{ field.type }} get{{ field.name | upper_camel_case }}() {
        return this.{{ field.name }};
    }

    public void set{{ field.name | upper_camel_case }}({{ field.type }} {{ field.name }}) {
        this.{{ field.name }} = {{ field.name }};
    }
    {% endfor %}
}
"""

dto = """
public class {{ ctx.entity.name }}Dto {
    {% for field in ctx.entity.fields %}
    private {{ field.type }} {{ field.name }};
    {% endfor %}

    {% for field in ctx.entity.fields %}
    public {{ field.type }} get{{ field.name|upper_camel_case }}() {
        return this.{{ field.name }};
    }

    public void set{{ field.name|upper_camel_case }}({{ field.type }} {{ field.name }}) {
        this.{{ field.name }} = {{ field.name }};
    }
    {% endfor %}
    
    public {{ctx.entity.name}} convertEntity() {
        {{ctx.entity.name}} {{ctx.table.name|lower_camel_case}} = new {{ctx.entity.name}}();
        {% for field in ctx.entity.fields %}
        {{ctx.table.name|lower_camel_case}}.set{{field.name|upper_camel_case}}(this.get{{field.name|upper_camel_case}}());
        {% endfor %}
        return {{ctx.table.name|lower_camel_case}};
    }
}
"""

mapper = """
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;

@Mapper 
public interface {{ctx.entity.name}}Mapper extends BaseMapper <{{ctx.entity.name}}> {}
"""

service = """
import com.baomidou.mybatisplus.extension.service.IService;

public interface {{ctx.entity.name}}Service extends IService<{{ctx.entity.name}}> {}
"""

service_impl = """
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class {{ctx.entity.name}}ServiceImpl extends ServiceImpl<{{ctx.entity.name}}Mapper, {{ctx.entity.name}}> implements {{ctx.entity.name}}Service {

    @Autowired
    private {{ ctx.table.name | upper_camel_case }}Mapper {{ ctx.table.name | lower_camel_case }}Mapper; 
}
"""

repository = """
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Objects;

@Repository
public class {{ctx.entity.name}}Repository {

    private final {{ ctx.table.name | upper_camel_case }}Mapper {{ ctx.table.name | lower_camel_case }}Mapper;
    private final {{ ctx.table.name | upper_camel_case }}Service {{ ctx.table.name | lower_camel_case }}Service; 

    public {{ctx.entity.name}}Repository({{ ctx.table.name | upper_camel_case }}Mapper {{ ctx.table.name | lower_camel_case }}Mapper, {{ ctx.table.name | upper_camel_case }}Service {{ ctx.table.name | lower_camel_case }}Service) {
        this.{{ ctx.table.name | lower_camel_case }}Mapper = {{ ctx.table.name | lower_camel_case }}Mapper;
        this.{{ ctx.table.name | lower_camel_case }}Service = {{ ctx.table.name | lower_camel_case }}Service;
    }

    private LambdaQueryWrapper<{{ctx.entity.name}}> getQueryWrapper({{ctx.entity.name}}Dto dto) {
        LambdaQueryWrapper<{{ctx.entity.name}}> query = new LambdaQueryWrapper();
        {% for field in ctx.entity.fields %}
        if (StringUtils.isNotBlank(dto.get{{field.name|upper_camel_case}}())) {
            query.eq({{ctx.entity.name}}::get{{field.name|upper_camel_case}}, dto.get{{field.name|upper_camel_case}}());
        }
        {% endfor %}
        return query;
    }

    public boolean create({{ctx.entity.name}}Dto dto) {
        {{ctx.entity.name}} {{ctx.table.name|lower_camel_case}} = dto.convertEntity();
        boolean result = this.{{ ctx.table.name | lower_camel_case }}Service.save({{ctx.table.name|lower_camel_case}});
        return result;
    }
    
    public boolean delete(Long id) {
        boolean result = false;
        {{ctx.entity.name}} {{ctx.table.name|lower_camel_case}} = this.{{ ctx.table.name | lower_camel_case }}Service.getById(id);
        if (Objects.nonNull({{ctx.table.name|lower_camel_case}})) {
            result = this.{{ ctx.table.name|lower_camel_case }}Service.removeById(id);
        }
        return result;
    }
    
    public boolean update({{ctx.entity.name}}Dto dto) {
        {{ctx.entity.name}} {{ctx.table.name|lower_camel_case}} = dto.convertEntity();
        boolean result = this.{{ ctx.table.name|lower_camel_case }}Service.updateById({{ctx.table.name|lower_camel_case}});
        return result;
    }

    public List<{{ctx.entity.name}}> list({{ctx.entity.name}}Dto dto) {
        LambdaQueryWrapper<{{ctx.entity.name}}> query = getQueryWrapper(dto);
        return this.{{ ctx.table.name|lower_camel_case }}Mapper.selectList(query);
    }

    public List<{{ctx.entity.name}}> list() {
        return this.{{ ctx.table.name|lower_camel_case }}Service.list();
    }
}
"""

tpls = {
    "entity": entity,
    "dto": dto,
    "mapper": mapper,
    "service": service,
    "service_impl": service_impl,
    "repository": repository,
}
