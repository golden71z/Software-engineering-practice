package com.campus.lostfound.common.result;

import lombok.Getter;

/**
 * 统一状态码定义
 * <p>
 * 编码规则：HTTP 语义前缀 + 业务序号
 * 200xx 成功、400xx 参数错误、401xx 认证错误、403xx 权限不足、404xx 资源不存在、500xx 服务异常
 */
@Getter
public enum ResultCode {

    SUCCESS(20000, "操作成功"),

    PARAM_ERROR(40000, "参数校验失败"),
    PARAM_MISSING(40001, "缺少必要参数"),
    PARAM_TYPE_ERROR(40002, "参数类型错误"),

    UNAUTHORIZED(40100, "未登录或登录已过期"),
    TOKEN_INVALID(40101, "登录凭证无效"),
    TOKEN_EXPIRED(40102, "登录凭证已过期"),

    FORBIDDEN(40300, "权限不足，无法操作"),
    ROLE_NOT_MATCH(40301, "当前角色无权访问该资源"),

    NOT_FOUND(40400, "请求的资源不存在"),
    USER_NOT_FOUND(40401, "用户不存在"),

    ERROR(50000, "系统繁忙，请稍后重试"),
    DB_ERROR(50001, "数据库操作失败"),
    FILE_UPLOAD_ERROR(50002, "文件上传失败");

    private final Integer code;
    private final String message;

    ResultCode(Integer code, String message) {
        this.code = code;
        this.message = message;
    }
}
