<template>
  <q-page class="index-page q-pa-lg">
    <!-- Заголовок -->
    <div class="text-center q-mb-xl">
      <h1 class="text-h3 text-weight-bold q-mb-md">Admin Dashboard</h1>
      <p class="text-h6 text-grey-7">Выберите в меню слева, что хотите редактировать</p>
    </div>

    <!-- Навигационные карточки -->
    <div class="row q-col-gutter-lg justify-center">
      <!-- About -->
      <div class="col-12 col-sm-6 col-md-4 col-lg-3">
        <q-card 
          class="nav-card cursor-pointer" 
          @click="$router.push('/about')"
        >
          <q-card-section class="text-center q-pa-xl">
            <q-icon name="info" size="64px" color="primary" class="q-mb-md" />
            <div class="text-h6 text-weight-medium">About</div>
            <div class="text-caption text-grey q-mt-sm">
              Управление информацией о себе
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Tech Stack -->
      <div class="col-12 col-sm-6 col-md-4 col-lg-3">
        <q-card 
          class="nav-card cursor-pointer" 
          @click="$router.push('/tech')"
        >
          <q-card-section class="text-center q-pa-xl">
            <q-icon name="code" size="64px" color="secondary" class="q-mb-md" />
            <div class="text-h6 text-weight-medium">Tech Stack</div>
            <div class="text-caption text-grey q-mt-sm">
              Управление технологиями и навыками
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Projects -->
      <div class="col-12 col-sm-6 col-md-4 col-lg-3">
        <q-card 
          class="nav-card cursor-pointer" 
          @click="$router.push('/projects')"
        >
          <q-card-section class="text-center q-pa-xl">
            <q-icon name="folder" size="64px" color="positive" class="q-mb-md" />
            <div class="text-h6 text-weight-medium">Projects</div>
            <div class="text-caption text-grey q-mt-sm">
              Управление проектами и портфолио
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Certificates -->
      <div class="col-12 col-sm-6 col-md-4 col-lg-3">
        <q-card 
          class="nav-card cursor-pointer" 
          @click="$router.push('/certificates')"
        >
          <q-card-section class="text-center q-pa-xl">
            <q-icon name="school" size="64px" color="warning" class="q-mb-md" />
            <div class="text-h6 text-weight-medium">Certificates</div>
            <div class="text-caption text-grey q-mt-sm">
              Управление сертификатами и достижениями
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Publications -->
      <div class="col-12 col-sm-6 col-md-4 col-lg-3">
        <q-card 
          class="nav-card cursor-pointer" 
          @click="$router.push('/publications')"
        >
          <q-card-section class="text-center q-pa-xl">
            <q-icon name="article" size="64px" color="info" class="q-mb-md" />
            <div class="text-h6 text-weight-medium">Publications</div>
            <div class="text-caption text-grey q-mt-sm">
              Управление публикациями и статьями
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Auth -->
      <div class="col-12 col-sm-6 col-md-4 col-lg-3">
        <q-card 
          class="nav-card cursor-pointer" 
          @click="$router.push('/auth')"
        >
          <q-card-section class="text-center q-pa-xl">
            <q-icon name="security" size="64px" color="negative" class="q-mb-md" />
            <div class="text-h6 text-weight-medium">User Management</div>
            <div class="text-caption text-grey q-mt-sm">
              Управление пользователями и ролями
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Comments -->
      <div class="col-12 col-sm-6 col-md-4 col-lg-3">
        <q-card 
          class="nav-card cursor-pointer" 
          @click="$router.push('/comments')"
        >
          <q-card-section class="text-center q-pa-xl">
            <q-icon name="chat" size="64px" color="deep-purple" class="q-mb-md" />
            <div class="text-h6 text-weight-medium">Comments</div>
            <div class="text-caption text-grey q-mt-sm">
              Модерация комментариев к проектам
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Notifications -->
      <div class="col-12 col-sm-6 col-md-4 col-lg-3">
        <q-card 
          class="nav-card cursor-pointer" 
          @click="$router.push('/notifications')"
        >
          <q-card-section class="text-center q-pa-xl">
            <q-icon name="notifications" size="64px" color="orange" class="q-mb-md" />
            <div class="text-h6 text-weight-medium">Notifications</div>
            <div class="text-caption text-grey q-mt-sm">
              Управление уведомлениями и email
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Статистика или быстрый обзор -->
    <div class="row q-mt-xl">
      <div class="col-12">
        <q-card class="bg-grey-1">
          <q-card-section>
            <div class="text-h6 q-mb-md">Быстрый доступ</div>
            <div class="row q-col-gutter-md">
              <div class="col-12 col-sm-4">
                <q-btn 
                  color="primary" 
                  icon="add" 
                  label="Новый проект" 
                  no-caps
                  class="full-width"
                  @click="$router.push('/projects')"
                />
              </div>
              <div class="col-12 col-sm-4">
                <q-btn 
                  color="secondary" 
                  icon="email" 
                  label="Отправить email" 
                  no-caps
                  class="full-width"
                  @click="$router.push('/notifications')"
                />
              </div>
              <div class="col-12 col-sm-4">
                <q-btn 
                  color="positive" 
                  icon="person_add" 
                  label="Добавить пользователя" 
                  no-caps
                  class="full-width"
                  @click="$router.push('/auth')"
                />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>
<style lang="scss" scoped>
.index-page {
  max-width: 1400px;
  margin: 0 auto;
}

.nav-card {
  transition: all 0.3s ease;
  height: 100%;
  
  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 25px rgba(0, 0, 0, 0.15);
  }
  
  .q-card__section {
    transition: background-color 0.3s ease;
  }
  
  &:hover .q-card__section {
    background-color: rgba(0, 0, 0, 0.02);
  }
}

// Адаптивность для мобильных устройств
@media (max-width: 599px) {
  .index-page {
    padding: 16px;
  }
  
  .nav-card {
    margin-bottom: 16px;
  }
}
</style>