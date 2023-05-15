import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RoomPreviewComponent } from './room-preview.component';

describe('RoomPreviewComponent', () => {
  let component: RoomPreviewComponent;
  let fixture: ComponentFixture<RoomPreviewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ RoomPreviewComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RoomPreviewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
