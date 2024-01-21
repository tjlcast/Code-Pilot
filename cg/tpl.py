#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time 2024/1/20 12:46
# @Name. Py
# @Author: jialtang


# 示例JSON数据
entity = """
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
    public {{ field.type }} get{{ field.name.title() }}() {
        return this.{{ field.name }};
    }

    public void set{{ field.name.title() }}({{ field.type }} {{ field.name }}) {
        this.{{ field.name }} = {{ field.name }};
    }
    {% endfor %}
    
    public static {{ctx.entity.name}} convertEntity() {
        {{ctx.entity.name}} {{ctx.table.name|lower_camel_case}} = new {{ctx.entity.name}}();
        {% for field in ctx.entity.fields %}
        {{ctx.table.name|lower_camel_case}}.set{{field.name|upper_camel_case}}(dto.get{{field.name|upper_camel_case}}());
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
public interface {{ctx.entity.name}}Service extends IService<{{ctx.entity.name}}> {}
"""

service_impl = """
@Service
public class {{ctx.entity.name}}Service extends ServiceImpl<{{ctx.entity.name}}Mapper, {{ctx.entity.name}}> implements {{ctx.entity.name}}Service {

    @Autowired
    private {{ ctx.table.name | upper_camel_case }}Mapper {{ ctx.table.name | lower_camel_case }}Mapper; 
}
"""

repository = """
@Repository
public class {{ctx.entity.name}}Repository {

    private final {{ ctx.table.name | upper_camel_case }}Mapper {{ ctx.table.name | lower_camel_case }}Mapper;
    private final {{ ctx.table.name | upper_camel_case }}Service {{ ctx.table.name | lower_camel_case }}Service; 

    public {{ctx.entity.name}}Repository({{ ctx.table.name | upper_camel_case }}Mapper {{ ctx.table.name | lower_camel_case }}Mapper, {{ ctx.table.name | upper_camel_case }}Serice {{ ctx.table.name | lower_camel_case }}Service) {
        this.{{ ctx.table.name | lower_camel_case }}Mapper = {{ ctx.table.name | lower_camel_case }}Mapper;
        this.{{ ctx.table.name | lower_camel_case }}Service = {{ ctx.table.name | lower_camel_case }}Service;
    }

    private LambdaQueryWrapper<{{ctx.entity.name}}> getQueryWrapper({{ctx.entity.name}}Dto dto) {
        LambdaQueryWrapper<{{ctx.entity.name}}> query = new LambdaQueryWrapper();
        {% for field in ctx.entity.fields %}
        if (StringUtils.isNotBlank(dto.get{{field.name|upper_camel_case}}()) {
            query.eq({{ctx.entity.name}}::get{{field.name|upper_camel_case}}, dto.get{{field.name|upper_camel_case}}())
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
            result = this.{{ ctx.table.name | lower_camel_case }}Service.removeById(id);
        }
        return result;
    }
    
    public boolean update({{ctx.entity.name}}Dto dto) {
        {{ctx.entity.name}} {{ctx.table.name|lower_camel_case}} = {{ctx.entity.name}}Dto.convertEntity();
        boolean result = this.{{ ctx.table.name | lower_camel_case }}Service.updateById({{ctx.table.name|lower_camel_case}});
        return result;
    }

    public List<{{ctx.entity.name}}> list({{ctx.entity.name}}Dto dto) {
        LambdaQueryWrapper<{{ctx.entity.name}}> query = getQueryWrapper(dto);
        return {{ ctx.table.name | upper_camel_case }}Mapper.selectList(query);
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
