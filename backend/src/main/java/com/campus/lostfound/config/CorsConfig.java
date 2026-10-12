package com.campus.lostfound.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.web.filter.CorsFilter;

/**
 * 跨域配置
 * <p>
 * 前后端分离架构下，前端（8090）与后端（8080）端口不同，属于跨域请求。
 * 开发阶段放开跨域；生产环境应通过 Nginx 反向代理统一域名，或收紧 allowedOriginPatterns。
 */
@Configuration
public class CorsConfig {

    @Bean
    public CorsFilter corsFilter() {
        CorsConfiguration config = new CorsConfiguration();
        // 允许的源（开发环境放开，生产环境需收紧为具体域名）
        config.addAllowedOriginPattern("*");
        // 允许携带凭证（Cookie / Authorization 头）
        config.setAllowCredentials(true);
        // 允许所有请求方法
        config.addAllowedMethod("*");
        // 允许所有请求头
        config.addAllowedHeader("*");
        // 暴露给前端的响应头
        config.addExposedHeader("Authorization");
        // 预检请求缓存时间（秒）
        config.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return new CorsFilter(source);
    }
}
